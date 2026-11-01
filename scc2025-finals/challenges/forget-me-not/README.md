# Forget Me Not [MISC]

Memory forensics challenge. A powershell script was run, using AES-256 to encrypt the image containing the flag. Key and IV were stored in the Windows Registry, and the encrypted flag in enviroment variable. Afterward, all files were deleted. You need to recover the encrypted flag, key, and IV from the memory dump and then decrypt the file to retrieve the flag. Solve script is available in the repository.

**FLAG: SCC{iv_got_99_problems_but_the_key_ain't_one}**