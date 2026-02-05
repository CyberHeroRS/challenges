# tested on IDA 9.1
# there are multiple ways to recover the graph, ida is not required, this is just a proof of concept

import re
import ida_funcs
import idautils

pat = re.compile(r"[EV][0-9]{1,2}")

def get_int(ins):
    cleaned = ins.split(";")[0].split(",")[-1].strip()
    if "h" in cleaned: return int(cleaned[:-1], 16)
    return int(cleaned)

def disasm(addr):
    f = ida_funcs.get_func(addr)
    out = []
    for ea in idautils.FuncItems(f.start_ea): out.append(idc.GetDisasm(ea))
    return out

typeinfo = {}
vtables = {}

# there is a lot of type RTTI type information in the binary, with names not stripped. lets us recover the classes and vtables
for addr, name in Names():
    n = demangle_name(name, True)
    if not n: continue
    nn = n.split("'")
    if len(nn) != 2: continue
    typ, nn = nn[0], nn[1] 
    if not re.match(pat, nn): continue
    if typ == "`typeinfo for":
        typeinfo[addr] = nn
    elif typ == "`vtable for":
        vtables[addr] = nn

# by the names, its clear we are dealing with a graph problem, so recover the graph
graph = {f"V{i}": [] for i in range(100)}

for addr, name in typeinfo.items():
    if "V" not in name: continue
    tmp = addr + 8
    while tmp not in typeinfo:
        curr = get_qword(tmp)
        if curr in typeinfo:
            graph[name].append(typeinfo[curr])
        tmp += 8

consts = {}
e_to_v = {}
Vconsts = {}

for addr, name in vtables.items():
    if "E" not in name: continue
    f1 = list(filter(lambda x: "call" in x, disasm(get_qword(addr + 16))))

    # some functions returning constants, being used as multipliers
    const = get_int(disasm(int(f1[1].split("_")[-1], 16))[4])
    consts[name] = const

    # loads vtable of some vertex, so must be constructor -> it inits all subclasses, then loads vtables
    # also calls constructors for parent classes -> gives us initial edge values
    f2 = disasm(int(f1[3].split("_")[-1], 16))
    vals = list(map(get_int, filter(lambda x: "mov" in x and "esi" in x, f2)))

    vtable_first = int(next(filter(lambda x: "lea" in x, f2)).split("_")[-1], 16) # first entry in vtable of some vertex -> vtable base is at addr - 16
    e_to_v[name] = vtables[vtable_first - 16] # i -> i map actually, so can be ignored
    Vconsts[vtables[vtable_first - 16]] = vals

# edge constructor takes value as argument, then multiplies it by the constant and adds it to running value

edge_vals = [consts[f"E{i}"] for i in range(100)]
vertex_vals = []

for i in range(100):
    a = Vconsts[f"V{i}"]
    b = [int(x[1:]) for x in graph[f"V{i}"]]
    vertex_vals.append(list(zip(b, a)))

# V99 checks for specific relatively small value -> try shortes path

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

        for next in vertex_vals[curr_node]:
            if next[0] not in visited:
                new_dist = curr_dist + edge_vals[next[0]] * next[1]
                if next[0] not in queue or new_dist < queue[next[0]][0]:
                    queue[next[0]] = (new_dist, curr_path + [next[0]])
    return 0, []

def pprint(vertex_vals, path):
    vx = [[v[0] for v in vv] for vv in vertex_vals]
    out = ""
    for i in range(len(path) - 1):
        out += str(vx[path[i]].index(path[i + 1]))
    return out + "f"

_, path = dijkstra(0, 99, (vertex_vals, edge_vals))
print(pprint(vertex_vals, path))
# 036504100332366350425525621303528785150f
