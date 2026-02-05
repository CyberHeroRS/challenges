# Vault

**Author** : tampon  
**Difficulty**: Easy  
**Description**: I got my hands on a password protected program that apparently contains a free flag. It should be easy work, but how do I enter the password!?

**Flag**: `SCC{2405de8b-943a-4770-ae08-5a467f82b176}`

## Writeup

Find `if ( startsWith((__int64)env, "key") && (unsigned __int8)endsWith(env, "3b6c0a1ddfb2eaf4") )` in main

```cmd
set key=3b6c0a1ddfb2eaf4
vault.exe
```
