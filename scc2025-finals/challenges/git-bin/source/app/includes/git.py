import os
import subprocess
from main import REPOS_DIR
GIT_PATH = '/usr/bin/git'

def git_command(repo_name, version, *args):
    dir_name = os.path.join(REPOS_DIR, repo_name)

    if not os.path.isdir(dir_name):
        return b'Repo not found'

    cmd = [GIT_PATH, *args]
    env = os.environ.copy()
    p = subprocess.Popen(' '.join(cmd), cwd=dir_name, env=env, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    p.wait()
    out = p.stdout.read()

    return out


def git_command_with_input(repo_name, version, input_data, *args):
    dir_name = os.path.join(REPOS_DIR, repo_name)

    if not os.path.isdir(dir_name):
        return b'Repo not found'
    env = os.environ.copy()
    cmd = [GIT_PATH, *args]
    p = subprocess.Popen(' '.join(cmd), cwd=dir_name, env=env, shell=True, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE)

    p.stdin.write(input_data)
    p.stdin.flush()
    for line in p.stdout:
        yield line