# REV - Side Quest
**Author** : Jovan Pavlovic  
**Difficulty**: <font color='yellow'>Medium</font>  
**Description**: You must defeat the evil king and bring back peace.

**Flag**: ``SCC{wh0_7h0u6h7_ch3351n6_w17h_51d3_ch4nn3l5_15_7h3_w4y_70_60}``

# Writeup
## Solution 1 - Side channel by counting instructions
```py
from pwn import *
import subprocess
import string

context.log_level='warn'

perf = "perf" #"/usr/lib/linux-tools/5.15.0-134-generic/perf"
binary = "./side-quest" 
charset = string.ascii_letters + string.digits + "{}_"
flag_length = 61
flag = ["?"] * flag_length
num_samples = 3

def measure_instructions(passphrase, runs=num_samples):
    return min(measure_instructions_proc(passphrase) for _ in range(runs))

def measure_instructions_proc(passphrase):
    cmd = f"{perf} stat -e instructions {binary}"
    p = process(cmd, shell=True)
    p.recvuntil(b"What would you like to do?")
    p.sendline(b"3")
    p.recvuntil(b"Passphrase:")
    p.sendline(passphrase.encode())
    p.sendline(b"4")
    output = p.recvall(timeout=1).decode(errors="ignore")
    p.close()
    for line in output.split("\n"):
        if "instructions" in line:
            try:
                return int(line.split()[0].replace(",", ""))
            except ValueError:
                return 0
    return -1

for i in range(flag_length):
    best_char = "?"
    best_instructions = 0

    for c in charset:
        test_flag = "".join(flag[:i]) + c + "?" * (flag_length - i - 1)
        instructions = measure_instructions(test_flag)

        print(test_flag, instructions)

        if instructions > best_instructions:
            best_instructions = instructions
            best_char = c

    flag[i] = best_char
    print(f"Current flag progress: {''.join(flag)}")

print(f"Final flag: {''.join(flag)}")
```

## Solution 2 - Reversing binary (understanding hash logic)
```rust
const HASHES: [&str; 61] = [
    "8de0b3c47f112c59745f717a626932264c422a7563954872e237b223af4ad643",
    "3a22ef4d24956d59cc29ab7830c590dee924d345708278860fe21f23a0bd2147",
    "5156cc64ad912a74bb8bd6a96ec955fa6d4fc4c4f97815d53e6eef9439d398a0",
    "ea1dbdddab56ea2e62296a4b895c9e3007a640c9e474f255f1214c8b4319dc9b",
    "2826939f4463f39635210203166f44788f60e76ae30dfc3eaf21c4f5fb87132e",
    "f47f139eacc273885ea9b100c502194722a62e29ea903092d33bcfaaa0461676",
    "cb5198bc6a3d24ee5e96c2e83415148827c59340aaca37aa0f99891ea6084f34",
    "72a7d42f7be19db29e6a87a141a114093ae1cc33f6be9213ae1f553bb4eda092",
    "632f3bce4292a5b176fdf6c5f401c7c9058cef0e97f210a8c39e4af3565f672d",
    "2cc67527f38a69dd9d3bb27a4300888e77baf8efb965719b680e85687dadddd4",
    "c22dff480d8a3bbee0cf45f46afe4d411d67039f3019dc2a82cc26be189f1822",
    "de6bb8a6ecadd2cfd3ebad410de1f182076394e0bed7c6283404a77555ee6641",
    "e887aa44eddf1426eacccc2f6fe7db541214288adbb6ceed324a09b1e3ed5c2f",
    "2e33d090a87851ab8fd117eb86b29a7900e126e3a9040af110aae75c266c66c4",
    "42ff460105527e7e70c09f3909032e7dde41615b0a00eb18425fd560a63434e1",
    "cd1cf6a3349e2ef351dcfad3ae4ab10f3f89bfd7eb391bf459e14d0c50749056",
    "a7b957419da8209ab147b46e41beea98a47458e712a3ac7a5bb88423106de949",
    "06035f31343782603b78a3a465cdf72d276292891f29a0943176c7f41a67ca92",
    "5c361554461044c443e9c4f7ba674baa917bd91c8465b982f2d63fd2c687ea6d",
    "428f2e50cd810ccbfb9778762c3409ffd7844ccdd583af3543c31e29478f54eb",
    "33f400c3a6f1baad31599de8675244ebc9620fcff731d90dbf697f83a443ec13",
    "e999e7955a2e3f7a271595d7d48f09d88674a19068bf742e9df7d5bd2766b5c1",
    "0898ed1fad8e37f75545d8940c0c4841c4d9cf8ec1b8cb91612be086fa80ea4b",
    "f4e13fd65cdeecd65891599e66f11eb7b87d9b0da88200f545ca25c60ff8883a",
    "05cc2c0600fa46add79a29defbbbc060b827ba57eff6c01c676ecfc92ea98a65",
    "171faf480b096a858757cbbb8c63ffe608bb5e2c02a161040457c4de275bd08f",
    "58e27d4e740568dc92404f6cfe2baca1df602d446f7c47358a5a99b9e477486e",
    "c0c874b44509e097b59c1555cfff39ff98eda2f7ff783327034c3dc0b49f8d68",
    "bfbd3c6606da03203b790b9632a31e635cfffb1ba9f61f90041050c526782356",
    "f696b5bdb2318c0cbe24625dc92c1e748e7d369799f246e9ed2ea2dff0da6df3",
    "0b88b1243b84ab282ec2f9ad77d40381be2c8062c48b4a5ce3468c66c64ed4db",
    "b4d401e61d0050d18eaaa07e502ac9e5ff43e6bb6bc7633203719620b0d4a7e4",
    "f0ce9fa40503ad677e726ed9d751c450ac24bd11df3b7d8403f0e53dd054d609",
    "07c304a9e07e9d64daa7d3b2e4a4f916cced506b0a3996c5ff654a9c62edd53f",
    "02087e5c5f0cda595021da7b5a454802ca53ddb1c7a0ea8e3b7d71109c93063e",
    "d83e2cabc6b2591e61965142f4bc8e9431f0361ff9580fb458c39ec585ef4450",
    "d188f418e24b5c79a07802db24a50e112c110c2835cde70de1b6b578675f1594",
    "24e265a39d1af0b7055b291f88749d1f27d35f7f0598aad9edad868fe840305e",
    "6d831e3c3cdd59040765ec12fbf7e53abd0b9eaee0616d37f43baaaa3eb35fa4",
    "78aa80d811e96e4e82bfd5bba0e609a04464de46d1957d2ea9c32f56569d6845",
    "f008b01d46507ccfbb5179e8dbdcdc3b65f203380c912854d7955187c4c5be5a",
    "36e79a09e14ec4a6f476b2b80705e15b7e2f1ae4a21a5b01901565af8b0dada5",
    "5d806ae8552fe3ad2c725eb8be8758d09702c7858bc8e536bf8fae460ea1cccb",
    "bf61043cc5dd97f63d35d7e4d7b120044f518ec96758cf8a64ded8a14021cc27",
    "a990672a739ce4a6b9f09447521e54025f306f520e111bbc692c666904b7568a",
    "06f6a5f1b2433693cc533a0de333007cdff338543f319dac368347a1154fe3dd",
    "5a6657b2de6483cf4ad951117a8005b5f10c0a174ac1488761bd4e9194b997bb",
    "9323d302c5906f9450580a4c3c7dc5a755151f3db50466877827641cfca5e341",
    "5ffe043f7281d46c6f5e9035734fb247f70cbcea14498ce526ea240193c45119",
    "61e621ab91e00a9bfbf4365c6d5b83fab0d5fa68842a52e429f37795ba10bc0d",
    "af4ab58f57cabdb621f96837c3eb8a672b3a5bd6bdc22d7165a7fe5eefb50cad",
    "8ab15dde770bc37c1e5103f596e948102a84355f4da8ad6c6b5f34c44a9c21cb",
    "3f7781aa6058b534883498ed7ff83b7ef3e0a751e30382f9e6d1ec4f32829163",
    "edd4bd6c2b2ec0877c36e32727ede138f6f32e290204eb74570fac222159063d",
    "c2a7a6d828719fe12d116bdba6e938a547d66061769084d5dabe7f935d5f07e6",
    "91ca13d4dd2c6e9b40005c9c3bca8335ad66da26de5ff26b811291be48ce27f4",
    "7070a6d2047c72fd41013e818e9172d07ff81fcf3b033842872b02f328e23c48",
    "61d9ee086bb3e457045a9b0ac8158dd85a93379d67f0657617bd5c7de038cbb1",
    "8503b5a6abb4e80f482e373d3d905ef4053caf77e2e47df88742c6a3952588ae",
    "335295a06f1de26588d4aebcb3a00362df185f2ce6480e33286be645806c9a3a",
    "2dcc8a58e9b832d4505a2070f268412b09de15f7826cfce73789f63bcbc092c3",
];

fn main() {
    let mut flag = String::new();

    for hash in HASHES {
        let c = guess_hashs(hash, &flag).unwrap();
        flag.push(c);
    }

    println!("Flag: {flag}");
}

fn guess_hashs(hash: &str, flag: &str) -> Option<char> {
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}_".chars() {
        let flag: String = format!("{flag}{c}").chars().rev().collect();
        if sha256::digest(flag) == hash {
            return Some(c);
        }
    }

    None
}
```