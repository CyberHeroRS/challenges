# secpwdgen

**Author** : Vucko
**Difficulty**: <font color='lightgreen'>Easy</font>  
**Description**: Secure password generator which uses username.

**External resources**:
- `main.rs` - [Download](public/main.rs)

**Flag**: ``SCC{y0u_sh0uld_b3_c4r3ful_w1th_4_byt3_utf8_ch4rs}``

# Writeup

Use 50 UTF-8 4 byte characters.
You can find them here: https://design215.com/toolbox/utf8-4byte-characters.php.

Payload:

$ python
Python 3.13.2 (main, Feb  5 2025, 08:05:21) [GCC 14.2.1 20250128] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> "𒀀" * 50
'𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀𒀀'
