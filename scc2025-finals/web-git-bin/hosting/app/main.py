import os
import subprocess
from shutil import copytree
import yaml
import random
import logging
import uuid
import re

from db import add_repo, remove_repo

REPO_DATA_FILE = ".repo.yml"

# FORMAT:
# HH:MM:SS [level]: message
formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger("agi")
logger.setLevel(logging.DEBUG)
# add custom formatter
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

uuid_v4_regex = re.compile(
    r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$",
    re.IGNORECASE,
)


def log(*args, level="info", **kwargs):
    # print(args, kwargs, file=sys.stderr, flush=True)
    if level == "error":
        logger.error(*args, **kwargs)
    elif level == "warning":
        logger.warning(*args, **kwargs)
    elif level == "debug":
        logger.debug(*args, **kwargs)
    else:
        logger.info(*args, **kwargs)


REPOS_DIR = "/repos"
REPO_TEMPLATES_DIR = "/repo-templates"

MY_URL = os.environ.get("MY_URL", "http://localhost")
PORT = os.getenv("PORT", 80)


def generate_password(length=16):
    """Generate a random password of given length."""
    characters = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789!@#$%^&*()-_=+[]{};:,.<>?/"
    )
    password = "".join(random.choice(characters) for _ in range(length))
    return password


def run(*args, cwd=None):

    p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    log(f"Running command: {args}", level="debug")

    return {
        "out": p.stdout.read().decode("utf-8"),
        "err": p.stderr.read().decode("utf-8"),
        "returncode": p.poll(),
    }


def git(repo_name, *args):
    return run(
        "git",
        f"--git-dir={REPOS_DIR}/{repo_name}/.git",
        f"--work-tree={REPOS_DIR}/{repo_name}",
        *args,
    )


def create_repo(repo_template: str, private: str = "off"):
    repo_name = str(uuid.uuid4())
    work_tree = f"{REPOS_DIR}/{repo_name}"
    repo_location = f"{REPOS_DIR}/{repo_name}/.git"

    password = generate_password()

    safe_template = os.path.normpath(f"{REPO_TEMPLATES_DIR}/{repo_template}")
    if not safe_template.startswith(REPO_TEMPLATES_DIR + '/') or not os.path.exists(
        safe_template
    ):
        log(f"Non-existent template: {repo_template}")
        return False, False

    # Git init
    ret = run("git", "init", work_tree, cwd=REPOS_DIR)
    if ret["returncode"] != 0:
        log(f'Error initializing git: {ret["err"]}')
        return False, False

    # Setup git hooks
    # (make symlink from all files in /app/hooks to .git/hooks)
    try:
        log(f"Setting up git hooks")
        hooks = os.listdir("/app/hooks")
        for hook in hooks:
            hook_path = f"/app/hooks/{hook}"
            hook_link = f"{repo_location}/hooks/{hook}"
            os.symlink(hook_path, hook_link)
    except Exception as e:
        log(f"Error setting up git hooks: {e}")
        return False, False

    # Copy repo template to worktree
    try:
        log(f"Copying repo template {repo_template} to {work_tree}")
        copytree(f"{REPO_TEMPLATES_DIR}/{repo_template}", work_tree, dirs_exist_ok=True)
        if os.path.exists(f"{work_tree}/hooks"):
            hooks = os.listdir(f"{work_tree}/hooks")
            for hook in hooks:
                os.rename(f"{work_tree}/hooks/{hook}", f"{repo_location}/hooks/{hook}")
            # remove hooks folder from worktree
            os.rmdir(f"{work_tree}/hooks")
    except FileExistsError:
        log(f"Repo {repo_name} already exists")
        return False, False
    except Exception as e:
        log(f"Error copying repo template: {e}")
        return False, False

    # add data to REPO_DATA_FILE
    repo_yml = f"{work_tree}/{REPO_DATA_FILE}"
    with open(repo_yml, "r") as f:
        repo_data = yaml.safe_load(f)
        repo_data["name"] = repo_name
        repo_data["private"] = private

    with open(repo_yml, "w") as f:
        yaml.dump(repo_data, f)

    # Git add and commit
    ret = git(repo_name, "add", ".")
    if ret["returncode"] != 0:
        return False, False

    ret = git(repo_name, "commit", "-m", "Initial commit", "--no-verify")

    log(ret)

    if ret["returncode"] != 0:
        return False, False

    try:
        add_repo(repo_name, password)
    except Exception as e:
        log(f"Error adding repo to database: {e}", level="error")
        return False, False

    return repo_name, password


def delete_repo(repo_name: str):
    if not uuid_v4_regex.match(repo_name):
        log(f"Invalid repo name: {repo_name}")
        return False
    if not os.path.exists(f"{REPOS_DIR}/{repo_name}"):
        log(f"Repo {repo_name} does not exist")
        return False
    try:
        log(f"Deleting repo {repo_name}")
        os.system(f"rm -rf {REPOS_DIR}/{repo_name}")

        remove_repo(repo_name)

        return True
    except Exception as e:
        log(f"Error deleting repo {repo_name}: {e}")
        return False


def get_repos():
    repos = [get_repo(repo) for repo in os.listdir(REPOS_DIR)]
    # remove None values
    return [repo for repo in repos if repo is not None]


def get_repo_data(repo_name: str):
    if not uuid_v4_regex.match(repo_name):
        log(f"Invalid repo name: {repo_name}")
        return {}
    if not os.path.exists(f"{REPOS_DIR}/{repo_name}"):
        log(f"Repo {repo_name} does not exist")
        return {}
    repo_yml = f"{REPOS_DIR}/{repo_name}/{REPO_DATA_FILE}"
    try:
        with open(repo_yml, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        log(f"Error reading repo data: {e}")
        return {}


def write_repo_data(repo_name: str, data: dict):
    repo_yml = f"{REPOS_DIR}/{repo_name}/{REPO_DATA_FILE}"
    with open(repo_yml, "w") as f:
        yaml.dump(data, f)


# Returns repo object
def get_repo(repo_name: str):
    if not uuid_v4_regex.match(repo_name):
        log(f"Invalid repo name: {repo_name}")
        return None
    if not os.path.exists(f"{REPOS_DIR}/{repo_name}"):
        log(f"Repo {repo_name} does not exist")
        return None

    # Get last commit hash and msg
    ret = git(repo_name, "log", "-1", "--pretty=format:%H %s")
    if ret["returncode"] != 0:
        log(f'Error getting last commit for repo {repo_name}: {ret["err"]}')
        return None

    commit_hash, commit_msg = ret["out"].split(" ", 1)
    commit_msg = commit_msg.strip()

    repo_data = get_repo_data(repo_name)

    return {
        "name": repo_name,
        # "last_commit": commit_hash, # Don't reveal commit hash
        "last_commit_msg": commit_msg,
        "data": repo_data,
    }


def commit_changes(repo_name: str, msg: str):
    ret = git(repo_name, "add", ".")
    if ret["returncode"] != 0:
        return False

    ret = git(repo_name, "commit", "-m", msg)
    if ret["returncode"] != 0:
        return False

    return True


def get_repo_templates():
    return os.listdir(REPO_TEMPLATES_DIR)
