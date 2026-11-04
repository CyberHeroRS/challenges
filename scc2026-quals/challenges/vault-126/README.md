## Challenge Name:

Vault 126

## Category:

Forensics

## Description:

> This is my first vibe-coded game. I hope you all like it and that it earns me a lot of money. 
> Players who reach a score of 274432 will receive a special reward, but please don't try to cheat or you will be banned.
> Following an internal audit of the workstation Admin-PC, a selective triage of forensic artifacts was performed to investigate a suspected unauthorized session. 

> Initial analysis suggests that a persistent session state may be preserved within the local environment. However, due to recent security hardening on the host, standard recovery procedures have proven unsuccessful. You are tasked with analyzing the provided filesystem structure to verify the identity of the active session.

>  Known Data:
>    - Target User: Admin-PC
>    - Known Password: Admin123
>    - Environment: Windows 10



## Flag:

* `SCC{n0_m0r3_m1lk_f0r_th3s3_3xp053d_c00k135}`

---

## Writeup:

### Step 1

Extract System Secrets: Use Mimikatz to extract the DPAPI_SYSTEM LSA secret from the SYSTEM and SECURITY registry hives. This is required to unlock the machine-level MasterKey.

### Step 2

Unlock the Machine MasterKey: Navigate to \Windows\System32\Microsoft\Protect\S-1-5-18\ and use the system secret to derive the machine's MasterKey.

### Step 3

Strip the App-Bound Header: Analyze the Local State file. The encrypted_key contains a Base64 string. Once decoded, the first 4 bytes (APPB) must be stripped to reveal the underlying DPAPI blob.

### Step 4

Decrypt the Inner Blob: Use the Machine MasterKey to decrypt the stripped blob. The result is not the AES key, but rather another DPAPI blob.

### Step 5

Unlock User MasterKey and Final Extraction: - Use the provided password `(Admin123)` and the user's SID to unlock the user's MasterKey located in `\Users\Admin-PC\AppData\Roaming\Microsoft\Protect\`.

* Use this User MasterKey to decrypt the "inner blob" from the previous step.

* The result is the raw 32-byte AES-256-GCM key.

### Step 6

Flag Recovery: Use the extracted AES key to decrypt the `Cookies` SQLite database. The flag is stored within the value of the `AuthToken` cookie, typically formatted as a JWT or Base64 string.
---
