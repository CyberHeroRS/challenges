import struct
import re
import sys


OPCODES = {
    "HALT":0,
    "ADD":1,"SUB":2,"MUL":3,"DIV":4,"MOD":5,"AND":6,"OR":7,"XOR":8,"NOT":9,
    "ADDI":10,"SUBI":11,"MULI":12,"DIVI":13,"MODI":14,"ANDI":15,"ORI":16,"XORI":17,
    "MOV":18,"SHL":19,"SHR":20,"ROL":21,"ROR":22,
    "LDR":23,"STR":24,
    "LDRI":25,"STRI":26,
    "LDRIR":27,"STRIR":28,
    "BIGADD":29,"BIGSUB":30,"BIGMUL":31,"BIGDIV":32,"BIGMOD":33,"BIGAND":34,"BIGOR":35,"BIGXOR":36,
    "BIGPOW":37,
    "BIGLDR":38,"BIGSTR":39,"BIGSHL":40,"BIGSHR":41,"BIGROL":42,"BIGROR":43,
    "CMP":44,"BIGCMP":45,
    "CMPI":46,
    "JMP":47,"JE":48,"JNE":49,"JL":50,"JLE":51,"JG":52,"JGE":53,"CALL":54,
    "RET":55,"SYSCALL":56,
    "PUSH":57,"POP":58,"BIGPUSH":59,"BIGPOP":60,
    "PUSHI":61,"POPI":62,
    "BIGMOV":63,
}

REGS = {f"R{i}":i for i in range(8)}

ESC = {
    r"\n":10, r"\r":13, r"\t":9,
    r"\\":92, r"\"":34, r"\0":0
}

def decode_string(s):
    out=[]
    i=0
    while i < len(s):
        if s[i]=="\\" and i+1<len(s):
            esc=s[i:i+2]
            if esc in ESC:
                out.append(ESC[esc])
                i+=2
                continue
        out.append(ord(s[i]))
        i+=1
    return out

def split_args(s):
    parts=[]
    cur=""
    in_str=False
    for c in s:
        if c=='"':
            in_str=not in_str
            cur+=c
        elif c=="," and not in_str:
            parts.append(cur.strip())
            cur=""
        else:
            cur+=c
    if cur:
        parts.append(cur.strip())
    return parts

def parse_dup(expr):
    m=re.match(r"(\d+)\s+dup\((.+)\)",expr,re.I)
    if not m:
        return None
    count=int(m.group(1))
    inner=m.group(2).strip()

    if inner.startswith('"'):
        vals=decode_string(inner[1:-1])
    else:
        vals=[int(inner,0)]

    return vals*count

def parse_data_line(line,data,labels):
    if ":" in line:
        label,rest=line.split(":",1)
        labels[label.strip()]=len(data)
        line=rest.strip()
        if not line:
            return

    tokens=line.split(None,1)
    if len(tokens)<2:
        return

    directive,args=tokens
    directive=directive.lower()

    values=[]

    for part in split_args(args):

        d=parse_dup(part)
        if d:
            values.extend(d)
            continue

        if part.startswith('"'):
            values.extend(decode_string(part[1:-1]))
        else:
            values.append(int(part,0))

    if directive=="db":
        for v in values:
            data.append(v & 0xFF)

    elif directive=="dw":
        for v in values:
            data+=struct.pack("<H",v)

    elif directive=="dd":
        for v in values:
            data+=struct.pack("<I",v)

    else:
        raise ValueError("Unknown data directive")

def type0(op): return op
def type1(op,rout,rin): return op | (rout<<6) | (rin<<9)
def type2(op,reg,imm): return op | (reg<<6) | ((imm & 0x7FFFFF)<<9)
def type3(op,imm): return op | ((imm & 0x3FFFFFF)<<6)
def type4(op,rout,rin,rmid): return op | (rout<<6)|(rin<<9)|(rmid<<12)
def type5(op,rout,rin,imm): return op | (rout<<6)|(rin<<9)|((imm & 0xFFFFF)<<12)

def reg(x): return REGS[x.upper()]

def parse_imm(x,labels):
    return labels[x] if x in labels else int(x,0)

def encode(line,labels):

    parts=re.split(r"[,\s]+",line.strip())
    op=parts[0].upper()
    opc=OPCODES[op]

    # Type0
    if op in ("HALT","RET","SYSCALL"):
        return type0(opc)

    # Type3
    if op in ("JMP","JE","JNE","JL","JLE","JG","JGE","CALL","PUSHI","POPI"):
        return type3(opc, parse_imm(parts[1],labels))

    # Type1
    if op in (
        "ADD","SUB","MUL","DIV","MOD","AND","OR","XOR",
        "CMP","BIGADD","BIGSUB","BIGMUL","BIGDIV",
        "BIGMOD","BIGAND","BIGOR","BIGXOR",
        "PUSH","POP","BIGPUSH","BIGPOP","LDR","STR",
        "BIGMOVR","BIGMOVB","MOVR", "BIGCMP"
    ):
        return type1(opc, reg(parts[1]), reg(parts[2]))

    # Type4
    if op=="BIGPOW":
        return type4(opc,reg(parts[1]),reg(parts[2]),reg(parts[3]))

    # Type5
    if op in ("LDRIR","STRIR"):
        return type5(opc,reg(parts[1]),reg(parts[2]),parse_imm(parts[3],labels))

    # Type2
    return type2(opc,reg(parts[1]),parse_imm(parts[2],labels))

def assemble(src,outfile):

    raw=[l.split(";")[0].strip() for l in open(src) if l.strip()]
    data=bytearray()
    code=[]
    labels={}
    section=None
    pc=0

    for line in raw:

        if line.lower()==".data":
            section="data"; continue
        if line.lower()==".code":
            section="code"; continue

        if section=="data":
            parse_data_line(line,data,labels)

        elif section=="code":

            if line.endswith(":"):
                labels[line[:-1]]=pc
            else:
                pc+=4

    section=None

    for line in raw:

        if line.lower()==".data":
            section="data"; continue
        if line.lower()==".code":
            section="code"; continue

        if section!="code":
            continue

        if line.endswith(":"):
            continue

        inst=encode(line,labels)
        code.append(struct.pack("<I",inst))

    code_bytes=b"".join(code)

    with open(outfile,"wb") as f:
        f.write(struct.pack("<I",len(data)))
        f.write(data)
        f.write(struct.pack("<I",len(code_bytes)))
        f.write(code_bytes)

    print(f"Data length: {len(data)}")
    print(f"Code length: {len(code_bytes)}")
    print("✔ Assembled:",outfile)

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Usage: python asm.py input.asm output.bin")
        sys.exit(1)

    assemble(sys.argv[1],sys.argv[2])
