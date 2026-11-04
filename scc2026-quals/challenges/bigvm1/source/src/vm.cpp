#include "vm.hpp"
#include <algorithm>
#include <sstream>
#include <cstdlib>
#include <vector>

VirtualMachine::VirtualMachine() : pc(0), sp(0), status(0) {
    std::memset(stack, 0, sizeof(stack));
    std::memset(code, 0, sizeof(code));
    std::memset(data, 0, sizeof(data));
    std::memset(regs, 0, sizeof(regs));
}

void VirtualMachine::init(const std::string& filename) {
    std::ifstream fp(filename, std::ios::binary | std::ios::in);
    if (!fp.good()) {
        throw std::runtime_error("Failed reading file");
    }
    
    uint32_t dataSize;
    fp.read(reinterpret_cast<char*>(&dataSize), sizeof(uint32_t));
    if (dataSize > DATA_SIZE) {
        throw std::runtime_error("Invalid DATA size");
    }
    fp.read(reinterpret_cast<char*>(data), dataSize);
    
    uint32_t codeSize;
    fp.read(reinterpret_cast<char*>(&codeSize), sizeof(uint32_t));
    if (codeSize > CODE_SIZE) {
        throw std::runtime_error("Invalid CODE size");
    }
    fp.read(reinterpret_cast<char*>(code), codeSize);
}

void VirtualMachine::run() {
    while (true) {
        Instruction instr;
        std::memcpy(&instr, code + pc, sizeof(uint32_t));
        
        uint32_t opcode_val = 0;
        std::memcpy(&opcode_val, code + pc, sizeof(uint32_t));
        instr = *reinterpret_cast<Instruction*>(&opcode_val);
        
        Opcodes opcode = static_cast<Opcodes>(instr.type0.opcode);

        switch (opcode) {
            case Opcodes::HALT:
                return;
                
            case Opcodes::ADD: {
                regs[instr.type1.rout] = regs[instr.type1.rin] + regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::SUB: {
                regs[instr.type1.rout] = regs[instr.type1.rin] - regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::MUL: {
                regs[instr.type1.rout] = regs[instr.type1.rin] * regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::DIV: {
                if (regs[instr.type1.rout] == 0) throw std::runtime_error("Division by zero");
                regs[instr.type1.rout] = regs[instr.type1.rin] / regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::MOD: {
                if (regs[instr.type1.rout] == 0) throw std::runtime_error("Modulo by zero");
                regs[instr.type1.rout] = regs[instr.type1.rin] % regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::AND: {
                regs[instr.type1.rout] = regs[instr.type1.rin] & regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::OR: {
                regs[instr.type1.rout] = regs[instr.type1.rin] | regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::XOR: {
                regs[instr.type1.rout] = regs[instr.type1.rin] ^ regs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::NOT: {
                regs[instr.type1.rout] = ~regs[instr.type1.rin];
                pc += 4;
                break;
            }
            
            case Opcodes::ADDI: {
                regs[instr.type2.reg] += instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::SUBI: {
                regs[instr.type2.reg] -= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::MULI: {
                regs[instr.type2.reg] *= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::DIVI: {
                if (instr.type2.imm == 0) throw std::runtime_error("Division by zero");
                regs[instr.type2.reg] /= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::MODI: {
                if (instr.type2.imm == 0) throw std::runtime_error("Modulo by zero");
                regs[instr.type2.reg] %= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::ANDI: {
                regs[instr.type2.reg] &= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::ORI: {
                regs[instr.type2.reg] |= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::XORI: {
                regs[instr.type2.reg] ^= instr.type2.imm;
                pc += 4;
                break;
            }
            
            case Opcodes::MOV: {
                regs[instr.type2.reg] = instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::SHL: {
                regs[instr.type2.reg] <<= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::SHR: {
                regs[instr.type2.reg] >>= instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::ROL: {
                uint32_t shift = instr.type2.imm % 32;
                regs[instr.type2.reg] = (regs[instr.type2.reg] << shift) | (regs[instr.type2.reg] >> (32 - shift));
                pc += 4;
                break;
            }
            case Opcodes::ROR: {
                uint32_t shift = instr.type2.imm % 32;
                regs[instr.type2.reg] = (regs[instr.type2.reg] >> shift) | (regs[instr.type2.reg] << (32 - shift));
                pc += 4;
                break;
            }
            
            case Opcodes::LDR: {
                uint32_t addr = regs[instr.type1.rin];
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data read out of bounds");
                std::memcpy(&regs[instr.type1.rout], data + addr, 4);
                pc += 4;
                break;
            }
            case Opcodes::STR: {
                uint32_t addr = regs[instr.type1.rin];
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data write out of bounds");
                std::memcpy(data + addr, &regs[instr.type1.rout], 4);
                pc += 4;
                break;
            }
            
            case Opcodes::LDRI: {
                uint32_t addr = instr.type2.imm;
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data read out of bounds");
                std::memcpy(&regs[instr.type2.reg], data + addr, 4);
                pc += 4;
                break;
            }

            case Opcodes::STRI: {
                uint32_t addr = instr.type2.imm;
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data write out of bounds");
                std::memcpy(data + addr, &regs[instr.type2.reg], 4);
                pc += 4;
                break;
            }
            
            case Opcodes::LDRIR: {
                uint32_t base = regs[instr.type5.rin];
                uint32_t addr = base + instr.type5.imm;
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data read out of bounds");
                std::memcpy(&regs[instr.type5.rout], data + addr, 4);
                pc += 4;
                break;
            }
            case Opcodes::STRIR: {
                uint32_t base = regs[instr.type5.rin];
                uint32_t addr = base + instr.type5.imm;
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data write out of bounds");
                std::memcpy(data + addr, &regs[instr.type5.rout], 4);
                pc += 4;
                break;
            }
            
            case Opcodes::BIGADD: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] + bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::BIGSUB: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] - bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::BIGMUL: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] * bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::BIGDIV: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] / bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::BIGMOD: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] % bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::BIGAND: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] & bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::BIGOR: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] | bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            case Opcodes::BIGXOR: {
                bregs[instr.type1.rout] = bregs[instr.type1.rin] ^ bregs[instr.type1.rout];
                pc += 4;
                break;
            }
            
            case Opcodes::BIGPOW: {
                bregs[instr.type4.rout] = bregs[instr.type4.rin].modpow(bregs[instr.type4.rout], bregs[instr.type4.rin], bregs[instr.type4.rmid]);
                pc += 4;
                break;
            }
            
            case Opcodes::BIGLDR: {
                uint32_t addr = instr.type2.imm;
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data read out of bounds");
                uint32_t size;
                std::memcpy(&size, data + addr, 4);
                if (addr + 4 + size * 4 > DATA_SIZE) throw std::runtime_error("BigInt data out of bounds");
                std::vector<uint32_t> vals;
                for (uint32_t i = 0; i < size; i++) {
                    uint32_t val;
                    std::memcpy(&val, data + addr + 4 + i * 4, 4);
                    vals.push_back(val);
                }
                bregs[instr.type2.reg].set_vals(vals);
                pc += 4;
                break;
            }
            case Opcodes::BIGSTR: {
                uint32_t addr = instr.type2.imm;
                if (addr > DATA_SIZE - 4) throw std::runtime_error("Data write out of bounds");
                uint32_t size = bregs[instr.type2.reg].size();
                if (addr + 4 + size * 4 > DATA_SIZE) throw std::runtime_error("Data segment too small for BigInt");
                std::memcpy(data + addr, &size, 4);
                for (uint32_t i = 0; i < size; i++) {
                    uint32_t val = bregs[instr.type2.reg].get_digit(i);
                    std::memcpy(data + addr + 4 + i * 4, &val, 4);
                }
                pc += 4;
                break;
            }
            case Opcodes::BIGSHL: {
                bregs[instr.type2.reg] = bregs[instr.type2.reg] << instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::BIGSHR: {
                bregs[instr.type2.reg] = bregs[instr.type2.reg] >> instr.type2.imm;
                pc += 4;
                break;
            }
            case Opcodes::BIGROL: {
                bregs[instr.type2.reg] = bregs[instr.type2.reg].rol(instr.type2.imm);
                pc += 4;
                break;
            }
            case Opcodes::BIGROR: {
                bregs[instr.type2.reg] = bregs[instr.type2.reg].ror(instr.type2.imm);
                pc += 4;
                break;
            }
            
            case Opcodes::CMP: {
                if (regs[instr.type1.rin] == regs[instr.type1.rout]) status = 0;
                else if (regs[instr.type1.rin] < regs[instr.type1.rout]) status = -1;
                else status = 1;
                pc += 4;
                break;
            }
            case Opcodes::BIGCMP: {
                if (bregs[instr.type1.rin] == bregs[instr.type1.rout]) status = 0;
                else if (bregs[instr.type1.rin] < bregs[instr.type1.rout]) status = -1;
                else status = 1;
                pc += 4;
                break;
            }
            case Opcodes::CMPI: {
                if (regs[instr.type2.reg] == instr.type2.imm) status = 0;
                else if (regs[instr.type2.reg] < instr.type2.imm) status = -1;
                else status = 1;
                pc += 4;
                break;
            }
            
            case Opcodes::JMP: {
                pc = instr.type3.imm;
                break;
            }
            case Opcodes::JE: {
                if (status == 0) pc = instr.type3.imm;
                else pc += 4;
                break;
            }
            case Opcodes::JNE: {
                if (status != 0) pc = instr.type3.imm;
                else pc += 4;
                break;
            }
            case Opcodes::JL: {
                if (status < 0) pc = instr.type3.imm;
                else pc += 4;
                break;
            }
            case Opcodes::JLE: {
                if (status <= 0) pc = instr.type3.imm;
                else pc += 4;
                break;
            }
            case Opcodes::JG: {
                if (status > 0) pc = instr.type3.imm;
                else pc += 4;
                break;
            }
            case Opcodes::JGE: {
                if (status >= 0) pc = instr.type3.imm;
                else pc += 4;
                break;
            }
            case Opcodes::CALL: {
                if (sp >= STACK_SIZE) throw std::runtime_error("Stack overflow");
                stack[sp++] = pc + 4;
                pc = instr.type3.imm;
                break;
            }
            
            case Opcodes::RET: {
                if (sp <= 0) throw std::runtime_error("Stack underflow");
                pc = stack[--sp];
                break;
            }
            
            case Opcodes::SYSCALL: {
                uint32_t addr, size;
                switch (regs[0]) {
                    case 0:
                        addr = regs[1];
                        size = regs[2];
                        if (size > DATA_SIZE || addr > DATA_SIZE - size)
                            throw std::runtime_error("Read data out of bounds");
                        regs[0] = read(0, &data[addr], size);
                        break;
                    case 1:
                        addr = regs[1];
                        size = regs[2];
                        if (size > DATA_SIZE || addr > DATA_SIZE - size)
                            throw std::runtime_error("Write data out of bounds");
                        regs[0] = write(1, &data[addr], size);
                        break;
                    case 2:
                        uint32_t filename = regs[1];
                        addr = regs[2];
                        size = regs[3];
                        if (filename >= DATA_SIZE)
                            throw std::runtime_error("Filename out of bounds");
                        if (size > DATA_SIZE || addr > DATA_SIZE - size)
                            throw std::runtime_error("Data out of bounds");
                        int fd = open((char*)&data[filename], 0, 0);
                        if (fd > 0) {
                            regs[0] = read(fd, &data[addr], size);
                            close(fd);
                        }
                        break;
                }
                pc += 4;
                break;
            }
            
            case Opcodes::PUSH: {
                if (sp >= STACK_SIZE) throw std::runtime_error("Stack overflow");
                stack[sp++] = regs[instr.type1.rin];
                pc += 4;
                break;
            }
            case Opcodes::POP: {
                if (sp <= 0) throw std::runtime_error("Stack underflow");
                regs[instr.type1.rout] = stack[--sp];
                pc += 4;
                break;
            }
            case Opcodes::BIGPUSH: {
                if (sp >= STACK_SIZE) throw std::runtime_error("Stack overflow");
                uint32_t size = bregs[instr.type1.rin].size();
                for (uint32_t i = 0; i < size; i++) {
                    stack[sp++] = bregs[instr.type1.rin].get_digit(size - 1 - i);
                }
                stack[sp++] = size;
                pc += 4;
                break;
            }
            case Opcodes::BIGPOP: {
                if (sp <= 0) throw std::runtime_error("Stack underflow");
                uint32_t size = stack[--sp];
                std::vector<uint32_t> vals;
                for (uint32_t i = 0; i < size; i++) {
                    vals.push_back(stack[--sp]);
                }
                bregs[instr.type1.rout].set_vals(vals);
                pc += 4;
                break;
            }
            case Opcodes::PUSHI: {
                if (sp >= STACK_SIZE) throw std::runtime_error("Stack overflow");
                stack[sp++] = instr.type3.imm;
                pc += 4;
                break;
            }
            case Opcodes::POPI: {
                if (sp < instr.type3.imm) throw std::runtime_error("Stack underflow");
                sp -= instr.type3.imm;
                pc += 4;
                break;
            }

            case Opcodes::BIGMOV: {
                bregs[instr.type2.reg] = instr.type2.imm;
                pc += 4;
                break;
            }
            
            default:
                throw std::runtime_error("Unknown opcode");
        }
    }
}