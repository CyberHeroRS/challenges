# Idea

## First exploit - leak using symlink

Server doesn't let you change the .repo.yml file, however it lets you change it's type to a symlink. This allows you to leak any file on the server, because the .repo.yml is displayed in the web interface - HOWEVER: it needs to be in valid yaml format. This means you need to create a symlink to a file that is valid yaml, and then link it to the file you want to leak.

First, we leak `/data/db/database.yml`. Using that, we know that the first repository is the one we're interested in (we get it's id).

Then, we can leak the `.git/refs/heads/main` file of that repository -> getting the object id of the commit.

## Second exploit - unprotected git-upload-pack endpoint

The git-upload-pack endpoint is unprotected, and allows us to get the contents of any file in the repository - as long as we know the object id of it.

We know the object id of the last commit in the flag repo, so we use this to get it. From that, we get its parent commit, that commit's tree, and the tree's contents. We can then get the contents of the file -> we read the flag.

# Usage of provided scripts

`python leak_file.py /repos/{FLAG_REPO_ID}/.git/refs/heads/main` -> leaks a specific file (it's badly written, so it sometimes fails and then reruns)

`python get_object.py {FLAG_REPO_ID} {object id}` -> leaks an object


`python main.py` -> full solve