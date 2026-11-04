.data
msg:  db "Enter your key: ", 0
key:  db 33 dup(0)

fail: db "Invalid character in key!", 0

exp: dd 0x1, 0xfc2a1b49
public: dd 0x20, 0xfd4e285, 0xda3b8b01, 0xf7578987, 0x71053d4b, 0x975d45e8, 0xe8e1929b, 0xef96f754, 0x3e9efa08, 0xb70e5ce4, 0xab6b6a47, 0xc021946a, 0xe9351f55, 0x7f08e52f, 0x8509ca48, 0xb73acc53, 0xa29aae4f, 0x831ea82c, 0x8af4d6e1, 0x8d36449f, 0xa4fcfee2, 0x2e09b445, 0x4ed06bbf, 0xc0ff6156, 0xf2c0c0a2, 0xbe0c39f4, 0x40cf0500, 0xede6b8f7, 0xd6370185, 0x741ffc8a, 0x219d62a5, 0x34ff27c7, 0x7c26da63
result: dd 0x20, 0x906016aa, 0x33fe6a0a, 0x279ad7aa, 0x2141a081, 0xe5652157, 0xae014bae, 0x29eb3395, 0x7a2e5351, 0x18e43bcc, 0x7d3cca38, 0xe763fac2, 0x79345837, 0x25ebc003, 0xf095d0, 0xb8ae1c3b, 0x1ab40232, 0xe0851ed, 0x5b36cc5c, 0xf5aa7a63, 0xf541e120, 0x66fd3e93, 0x1f5d4ea, 0xeb865d9c, 0x3f58eddc, 0x7cadad41, 0x849b93f9, 0xd5dff743, 0x67503b94, 0xfc8e57f, 0x18cffefa, 0x823273eb, 0x369a1673

resfail: db "Key verification failed!", 10
end: db "Flag: "
file: db "flag.txt"

flag: db 64 dup(0)

.code
start:
    mov r0, 1
    mov r1, msg
    mov r2, 17
    syscall

    mov r0, 0
    mov r1, key
    mov r2, 32
    syscall

    mov r0, key
    mov r3, 0

loopstart:
    ldrir r1, r0, 0
    call getcode
    push r1, r1
    pushi 1
    bigshl r2, 5
    bigpop r1, r1
    bigor r2, r1
    addi r0, 1
    addi r3, 1
    cmpi r3, 32
    jl loopstart

    bigldr r1, public
    bigldr r3, exp
    bigldr r4, result

    bigpow r2, r3, r1

    bigcmp r2, r4
    jne bigfail

    mov r0, 1
    mov r1, end
    mov r2, 6
    syscall

    mov r0, 2
    mov r1, file
    mov r2, flag
    mov r3, 64
    syscall

    push r0, r0
    pop r2, r2
    mov r0, 1
    mov r1, flag
    syscall

    halt

bigfail:
    mov r0, 1
    mov r1, resfail
    mov r2, 25
    syscall
    halt

getcode:
    andi r1, 0xff
    cmpi r1, 0x41
    jl checkdig
    cmpi r1, 0x5a
    jg checkdig
    subi r1, 0x41
    ret
checkdig:
    cmpi r1, 0x32
    jl charfail
    cmpi r1, 0x37
    jg charfail
    subi r1, 0x32
    addi r1, 26
    ret
charfail:
    mov r0, 1
    mov r1, fail
    mov r2, 26
    syscall
    halt