"""Standalone (no-IDA) reimplementation of the RTTI/vtable graph-recovery and
shortest-path algorithm originally prototyped with IDAPython (see the history
in sol.py). It parses the real ELF binary directly with pyelftools and
disassembles the handful of tiny helper functions it needs with Capstone, then
runs the exact same Dijkstra shortest-path search, so the magic input string
is genuinely derived from the binary every time this module is imported --
there is no precomputed/hardcoded shortcut anywhere in this file.

Background: `isthisjava` encodes a fixed directed graph by (ab)using one C++
class per vertex/edge, with multiple inheritance and virtual dispatch
standing in for graph edges (see source/gen.py / source/src.cpp). Vertex
classes are named V0..V99, edge classes E0..E99. Class `Vi` multiply-inherits
from `Vertex` plus one `Ej` per outgoing edge; `Ej::next()` multiplies the
running value by a per-edge constant, adds it, and constructs the next `Vj`
with per-base-class initial weights. Reaching V99 with the right accumulated
value (found via shortest path from V0) prints the flag, which is why we only
need to recover the graph and replay Dijkstra, exactly like the original
IDAPython script did.

Steps, each a direct, non-IDA analogue of the matching step in the IDAPython
prototype:

1. Itanium C++ ABI RTTI stores each class's demangled "typeinfo name" as a
   raw `<len><identifier>` string (e.g. "3V42"), unrelated to any symbol
   table -- so even on a fully stripped binary we find all 200 of them
   directly in `.rodata` with a regex, giving us name-string address -> name.
2. Each `typeinfo` struct is `{vtable_ptr, name_ptr, ...bases}`; we find every
   qword in `.data.rel.ro` that points at one of those name strings -- that
   qword lives at typeinfo_addr+8, giving us typeinfo struct address -> name
   (this replaces walking IDA's auto-named `Names()` RTTI entries).
3. For each `Vi` typeinfo, we replicate the IDAPython "walk forward 8 bytes
   at a time until the address itself is another known typeinfo" trick to
   recover its ordered list of `Ej` base classes (its graph adjacency),
   since `__vmi_class_type_info` base-class descriptors have variable length
   depending on the (variable) number of multiply-inherited edges.
4. Each `Ei`'s own vtable is found the same way (a qword pointing at `Ei`'s
   typeinfo sits at vtable_addr+8), filtered to candidates whose first
   virtual-function slot (vtable_addr+16) actually points into `.text`
   (this discards the base-class-pointer slots inside `Vi` typeinfo structs,
   which also reference `Ei`'s typeinfo address but aren't vtables).
5. We disassemble `Ei::next()` (the function pointer at vtable_addr+16) with
   Capstone to find its `call` instructions: the 2nd call is to `Ei`'s
   private `getX()` (whose body is a single `mov eax, imm32` -- the edge
   multiplier constant) and the 4th call is to the freshly-constructed `Vi`'s
   constructor, whose `mov esi, imm32` instructions (in order) are the
   initial weights passed to each inherited edge's base-class constructor,
   lining up positionally with the adjacency list from step 3.
6. With the full weighted graph reconstructed, we run the identical
   Dijkstra shortest-path search from V0 to V99 used in gen.py/the original
   IDAPython script, and format the resulting path into the magic input
   string the exact same way.
"""

import re
import struct

from capstone import CS_ARCH_X86, CS_MODE_64, CS_OP_IMM, CS_OP_REG, Cs
from elftools.elf.elffile import ELFFile

NUM_VERTICES = 100
TYPEINFO_NAME_RE = re.compile(rb"(\d+)([EV]\d{1,2})\x00")


def _disasm_func(md, text_data, tbase, addr, max_len=0x400):
    """Disassemble linearly from addr until (and including) a ret."""
    off = addr - tbase
    insns = []
    for ins in md.disasm(text_data[off : off + max_len], addr):
        insns.append(ins)
        if ins.mnemonic == "ret":
            break
    return insns


def _call_targets(insns):
    out = []
    for ins in insns:
        if ins.mnemonic == "call" and ins.operands and ins.operands[0].type == CS_OP_IMM:
            out.append(ins.operands[0].imm)
    return out


def _imm32_movs_to(insns, regname):
    """mov <regname>, imm32 instructions, in program order."""
    out = []
    for ins in insns:
        if ins.mnemonic != "mov" or len(ins.operands) != 2:
            continue
        dst, src = ins.operands
        if dst.type == CS_OP_REG and src.type == CS_OP_IMM:
            if ins.reg_name(dst.reg) == regname:
                out.append(src.imm)
    return out


def recover_graph(binary_path):
    """Parse the isthisjava binary and return (vertex_vals, edge_vals):
    vertex_vals[i] is a list of (neighbor_vertex_index, weight) tuples (in
    the order the solver needs to print, matching the original script), and
    edge_vals[i] is the Ei multiplier constant.
    """
    elf = ELFFile(open(binary_path, "rb"))

    rodata = elf.get_section_by_name(".rodata")
    rodata_data = rodata.data()
    rbase = rodata["sh_addr"]

    drr = elf.get_section_by_name(".data.rel.ro")
    drr_data = drr.data()
    dbase = drr["sh_addr"]

    text = elf.get_section_by_name(".text")
    text_data = text.data()
    tbase = text["sh_addr"]
    text_lo, text_hi = tbase, tbase + len(text_data)

    def get_qword(addr):
        off = addr - dbase
        if 0 <= off < len(drr_data) - 8:
            return struct.unpack_from("<Q", drr_data, off)[0]
        return None

    # Step 1: typeinfo name strings in .rodata ("<len><ident>\0").
    names = {}
    for m in TYPEINFO_NAME_RE.finditer(rodata_data):
        length = int(m.group(1))
        ident = m.group(2).decode()
        if length == len(ident):
            names[rbase + m.start()] = ident
    if len(names) != 2 * NUM_VERTICES:
        raise AssertionError(
            f"expected {2 * NUM_VERTICES} typeinfo name strings, found {len(names)}"
        )
    name_addrs = set(names.keys())

    # Step 2: typeinfo struct addresses, via backreferences to those names.
    typeinfo = {}
    for off in range(0, len(drr_data) - 8, 8):
        val = struct.unpack_from("<Q", drr_data, off)[0]
        if val in name_addrs:
            typeinfo[dbase + off - 8] = names[val]
    if len(typeinfo) != 2 * NUM_VERTICES:
        raise AssertionError(
            f"expected {2 * NUM_VERTICES} typeinfo structs, found {len(typeinfo)}"
        )

    # Step 3: Vi -> ordered [Ej, ...] adjacency, from vmi_class_type_info
    # base-class pointer slots.
    graph = {f"V{i}": [] for i in range(NUM_VERTICES)}
    for addr, name in typeinfo.items():
        if "V" not in name:
            continue
        tmp = addr + 8
        while tmp not in typeinfo:
            curr = get_qword(tmp)
            if curr is not None and curr in typeinfo:
                graph[name].append(typeinfo[curr])
            tmp += 8
    for i in range(NUM_VERTICES):
        if not graph[f"V{i}"]:
            raise AssertionError(f"V{i} has no recovered edges")

    # Step 4: Ei vtable addresses, via backreferences to Ei's typeinfo addr,
    # filtered to the one whose first vfunc slot lands inside .text.
    vtables = {}
    for off in range(0, len(drr_data) - 8, 8):
        val = struct.unpack_from("<Q", drr_data, off)[0]
        if val in typeinfo and "E" in typeinfo[val]:
            vtable_addr = dbase + off - 8
            fptr = get_qword(vtable_addr + 16)
            if fptr is not None and text_lo <= fptr < text_hi:
                vtables.setdefault(typeinfo[val], []).append(fptr)
    for i in range(NUM_VERTICES):
        if len(vtables.get(f"E{i}", [])) != 1:
            raise AssertionError(f"E{i}: expected exactly 1 vtable, got {vtables.get(f'E{i}')}")

    # Step 5: disassemble Ei::next() to recover the edge constant (getX())
    # and the Vi constructor's per-base-class initial weights.
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    edge_vals = {}
    vertex_ctor_vals = {}
    for i in range(NUM_VERTICES):
        fptr = vtables[f"E{i}"][0]
        insns = _disasm_func(md, text_data, tbase, fptr)
        calls = _call_targets(insns)
        if len(calls) < 4:
            raise AssertionError(f"E{i}::next(): expected >=4 calls, got {len(calls)}")
        getx_target, ctor_target = calls[1], calls[3]

        getx_insns = _disasm_func(md, text_data, tbase, getx_target)
        consts = _imm32_movs_to(getx_insns, "eax")
        if len(consts) != 1:
            raise AssertionError(f"E{i}::getX(): expected 1 constant, got {consts}")
        edge_vals[i] = consts[0]

        ctor_insns = _disasm_func(md, text_data, tbase, ctor_target)
        vertex_ctor_vals[i] = _imm32_movs_to(ctor_insns, "esi")

    for i in range(NUM_VERTICES):
        if len(vertex_ctor_vals[i]) != len(graph[f"V{i}"]):
            raise AssertionError(
                f"V{i}: {len(vertex_ctor_vals[i])} ctor weights vs "
                f"{len(graph[f'V{i}'])} adjacent edges"
            )

    vertex_vals = []
    for i in range(NUM_VERTICES):
        edges = [int(x[1:]) for x in graph[f"V{i}"]]
        weights = vertex_ctor_vals[i]
        vertex_vals.append(list(zip(edges, weights)))

    edge_vals_list = [edge_vals[i] for i in range(NUM_VERTICES)]
    return vertex_vals, edge_vals_list


def dijkstra(start, end, graph):
    vertex_vals, edge_vals = graph
    visited = set()
    queue = {start: (0, [start])}

    while queue:
        curr_node = min(queue, key=lambda x: queue.get(x)[0])
        curr_dist, curr_path = queue.pop(curr_node)
        visited.add(curr_node)
        if curr_node == end:
            return curr_dist, curr_path

        for nxt in vertex_vals[curr_node]:
            if nxt[0] not in visited:
                new_dist = curr_dist + edge_vals[nxt[0]] * nxt[1]
                if nxt[0] not in queue or new_dist < queue[nxt[0]][0]:
                    queue[nxt[0]] = (new_dist, curr_path + [nxt[0]])
    return 0, []


def pprint_path(vertex_vals, path):
    vx = [[v[0] for v in vv] for vv in vertex_vals]
    out = ""
    for i in range(len(path) - 1):
        out += str(vx[path[i]].index(path[i + 1]))
    return out + "f"


def compute_magic_input(binary_path):
    vertex_vals, edge_vals = recover_graph(binary_path)
    _, path = dijkstra(0, NUM_VERTICES - 1, (vertex_vals, edge_vals))
    if not path:
        raise AssertionError("dijkstra found no path from V0 to V99")
    return pprint_path(vertex_vals, path).encode()
