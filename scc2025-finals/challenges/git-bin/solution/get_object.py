import requests
import subprocess
import sys
import os
import random
import string
REPO = random.choice(string.ascii_lowercase) + ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

""" def get_ref_sha(repo_url, ref_name):
    # Construct the URL for the info/refs endpoint
    info_refs_url = f"{repo_url}/info/refs?service=git-upload-pack"

    # Send the GET request to fetch refs
    response = requests.get(info_refs_url)

    # Check for a successful response
    if response.status_code != 200:
        print(f"Error: Unable to fetch refs, HTTP status code {response.status_code}")
        return None

    # The response should be pkt-line encoded
    refs_data = response.text.splitlines()

    # Find the specific ref and extract the SHA
    for line in refs_data:
        if ref_name in line:
            sha = line.split()[0]
            return sha

    # If the ref is not found
    print(f"Error: Ref '{ref_name}' not found.")
    return None """


def create_request_dat(sha, file_name="request.dat"):
    """Create the pkt-line request.dat file with the provided SHA."""
    pkt_line = f"0032want {sha}\n00000009done\n"

    # Write the pkt-line data to a file
    with open(file_name, "w") as file:
        file.write(pkt_line)

    print(f"Request file created: {file_name}")

def send_request_and_get_response(repo_url, file_name="request.dat"):
    """ Send the request file and print the response. """
    # Read the contents of request.dat
    with open(file_name, 'rb') as file:
        request_data = file.read()
    
    # Send the POST request with the request data
    response = requests.post(
        f"{repo_url}/git-upload-pack",
        headers={
            "Content-Type": "application/x-git-upload-pack-request",
            "Accept": "application/x-git-upload-pack-result"
        },
        data=request_data
    )
    
    # Check if the response was successful
    if response.status_code == 200:
        """ print("Response received successfully.")
        # Print part of the response to inspect
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response body (first 500 bytes): {response.content[:500]}")  # Print first 500 bytes of the response body
        # Optionally, save the packfile """
        with open("response.pack", "wb") as f:
            f.write(response.content)
    else:
        print(f"Error: {response.status_code} - {response.text}")

def unpack_response(file_name="response.pack"):
    # Clean the response by removing the first line
    with open(file_name, "rb") as f:
        response_data = f.readlines()

    # Remove the first line
    cleaned_data = b"".join(response_data[1:])

    # Write the cleaned data back to the file
    with open(file_name, "wb") as f:
        f.write(cleaned_data)

    #print(f"Cleaned the response file: {file_name}")
    # Ensure the repository directory exists
    repo_dir = REPO + ".git"
    if os.path.exists(repo_dir):
        #print(f"Repository directory '{repo_dir}' already exists. Removing it.")
        subprocess.run(["rm", "-rf", repo_dir], check=True)
    # Initialize a new bare repository
    subprocess.run(["git", "init", "--bare", repo_dir], check=True)
    #print(f"Initialized a new bare repository: {repo_dir}")


    # Unpack the packfile using git index-pack
    subprocess.run(["git", "-C", repo_dir, "index-pack", '../' + file_name], check=True)
    #print(f"Unpacked the packfile: {file_name}")

    # Ensure the pack/ directory exists
    pack_dir = os.path.join(repo_dir, "objects", "pack")
    os.makedirs(pack_dir, exist_ok=True)

    # Move .idx file to pack/ directory
    idx_file = os.path.basename(file_name).replace(".pack", ".idx")
    idx_file_path = os.path.join(os.getcwd(), idx_file)
    if os.path.exists(idx_file_path):
        #print(f"Moving {idx_file_path} to {pack_dir}")
        subprocess.run(["mv", idx_file_path, pack_dir], check=True)
    else:
        print(f"Index file {idx_file_path} does not exist.")

    # Move .pack file to pack/ directory
    pack_file_path = os.path.join(os.getcwd(), file_name)
    if os.path.exists(pack_file_path):
        #print(f"Moving {pack_file_path} to {pack_dir}")
        subprocess.run(["mv", pack_file_path, pack_dir], check=True)
    else:
        print(f"Pack file {pack_file_path} does not exist.")




def get_remote_ref_raw(repo_name, ref_name):
    """
    Process a Git repository by fetching a specific ref and unpacking the response.

    Args:
        repo_name (str): The name of the repository.
        ref_name (str): The ref to fetch (e.g., 'refs/heads/main').
    """
    repo_url = f"http://{os.environ['SERVICE_APP_HTTP_HOST']}:{os.environ['SERVICE_APP_HTTP_PORT']}/git/{repo_name}"

    # Create the request.dat file
    create_request_dat(ref_name)

    # Send the request and get the response
    send_request_and_get_response(repo_url)

    unpack_response("response.pack")

    # git cat-file -e <sha> <file_path>
    catproc = subprocess.run(
        ["git", "-C", REPO + ".git", "cat-file", "-p", ref_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if catproc.returncode != 0:
        print(f"Error: {catproc.stderr.decode()}")
        return
    data =catproc.stdout.decode()

    # Clean up
    subprocess.run(["rm", "-rf", REPO + ".git"], check=True)
    subprocess.run(["rm", "-rf", "response.pack"], check=True)
    subprocess.run(["rm", "-rf", "request.dat"], check=True)

    return data

    

if __name__ == "__main__":
    # Check if the script is being run directly
    if len(sys.argv) != 3:
        print("Usage: python get_object.py <repo_name> <ref_name>")
        sys.exit(1)

    repo_name = sys.argv[1]
    ref_name = sys.argv[2]

    # Call the function with the provided arguments
    data = get_remote_ref_raw(repo_name, ref_name)
    print(data)