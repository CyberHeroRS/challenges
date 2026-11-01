# cxorruption

**Author**: Vucko  
**Difficulty**: <font color='lightgreen'>Very Easy</font>  
**Description**: At our company all our files were corrupted with this binary. Could you help us reverse this cxorruption scheme and recover our files?  
**Infrastructure requirements**: zip  

Flag: `SCC{x0r_15_700_345y_70_d3c1ph3r}`

## Solution
This binary is compiled with –O0 -g.  
Just open binary in decompiler, it should be pretty readable C code:  

```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  char v3; // r12
  int i; // [rsp+8h] [rbp-A8h]
  int i_0; // [rsp+Ch] [rbp-A4h]
  FILE *flag; // [rsp+10h] [rbp-A0h]
  unsigned __int64 size; // [rsp+18h] [rbp-98h]
  FILE *enc; // [rsp+28h] [rbp-88h]
  char buff[100]; // [rsp+30h] [rbp-80h] BYREF
  unsigned __int64 v11; // [rsp+98h] [rbp-18h]

  v11 = __readfsqword(0x28u);
  flag = fopen("./flag.txt", "r");
  memset(buff, 0, sizeof(buff));
  size = fread(buff, 1uLL, 0x64uLL, flag);
  for ( i = 0; i < size - 1; ++i )
    buff[i] += buff[i + 1];
  for ( i_0 = 0; i_0 < size; ++i_0 )
  {
    v3 = buff[i_0];
    buff[i_0] = aSecretKey[i_0 % strlen("SECRET_KEY")] ^ v3;
  }
  enc = fopen("./enc.txt", "wb");
  fwrite(buff, 1uLL, size, enc);
  return 0;
}
```

After reversing math, our python solver script will look like this:  

```py
enc = open("../challenge/enc.txt", "rb").read()
secret_key = b"SECRET_KEY"

dec = []
for i, x in enumerate(enc):
    dec += [x ^ secret_key[i % len(secret_key)]]


for i in range(len(dec) - 1, 0, -1):
    dec[i - 1] -= dec[i]


print("".join([chr(i) for i in dec]))
```
