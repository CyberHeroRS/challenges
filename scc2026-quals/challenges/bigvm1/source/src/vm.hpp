#ifndef VM_HPP
#define VM_HPP

#include "bigint.hpp"
#include <iostream>
#include <fstream>
#include <stdexcept>
#include <cstring>
#include <iomanip>
#include <print>

#include <unistd.h>
#include <fcntl.h>

#define STACK_SIZE 4096
#define CODE_SIZE 8192
#define DATA_SIZE 4096

enum class Opcodes
{
    HALT, // Type0
    ADD, SUB, MUL, DIV, MOD, AND, OR, XOR, NOT, // Type1
    ADDI, SUBI, MULI, DIVI, MODI, ANDI, ORI, XORI, // Type2
    MOV, SHL, SHR, ROL, ROR, // Type2
    LDR, STR, // Type1
    LDRI, STRI, // Type2
    LDRIR, STRIR, // Type5
    BIGADD, BIGSUB, BIGMUL, BIGDIV, BIGMOD, BIGAND, BIGOR, BIGXOR, // Type1
    BIGPOW, // Type4
    BIGLDR, BIGSTR, BIGSHL, BIGSHR, BIGROL, BIGROR, // Type2
    CMP, BIGCMP, // Type1
    CMPI, // Type2
    JMP, JE, JNE, JL, JLE, JG, JGE, CALL, // Type3
    RET, SYSCALL, // Type0
    PUSH, POP, BIGPUSH, BIGPOP, // Type1
    PUSHI, POPI, // Type3
    BIGMOV, // Type2
};

struct Type0 {
    uint32_t opcode : 6;
};

struct Type1 {
    uint32_t opcode : 6;
    uint32_t rout : 3;
    uint32_t rin : 3;
};

struct Type2 {
    uint32_t opcode : 6;
    uint32_t reg : 3;
    uint32_t imm : 23;
};

struct Type3 {
    uint32_t opcode : 6;
    uint32_t imm : 26;
};

struct Type4 {
    uint32_t opcode : 6;
    uint32_t rout : 3;
    uint32_t rin : 3;
    uint32_t rmid : 3;
};

struct Type5 {
    uint32_t opcode : 6;
    uint32_t rout : 3;
    uint32_t rin : 3;
    int imm : 20;
};

union Instruction {
    Type0 type0;
    Type1 type1;
    Type2 type2;
    Type3 type3;
    Type4 type4;
    Type5 type5;
};

class VirtualMachine
{
public:
    VirtualMachine();
    void init(const std::string& filename);
    void run();

private:
    uint32_t stack[STACK_SIZE];
    uint8_t code[CODE_SIZE];
    uint8_t data[DATA_SIZE];

    uint32_t regs[8];
    BigInt bregs[8];
    int pc;
    int sp;
    int status;
};

#endif // VM_HPP