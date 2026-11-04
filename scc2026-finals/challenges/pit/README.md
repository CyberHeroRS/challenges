# web-pit

**Category:** web  
**Author:** franga2000

## Description

You threw your files into the pit and they came out...sticky

## Writeup

### Vulnerability

The file storage app allows users to create and extract zip and tar archives. The tar command supports symlinks and saves them as-is, while the zip command resolves them to their target files. 

### Intended solution

The attacker can upload a tar file containing a symlink to a sensitive file and extract it, which creates a real symlink on the server. The file download feature checks for path traversal, so the file still can't be accessed, but the attacker can use the zip feature to zip that same directory, which will resolve the symlink and include the target file in the zip archive. The attacker can then download the zip and read the contents of the sensitive file.

See `solv.py`.
