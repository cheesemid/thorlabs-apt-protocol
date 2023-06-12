
from . import cmd_defs
import struct

pack_cmds = type("", (), {})()

implemented_prefixes = ["hub", "hw", "kna", "kpz", "ksg", "la", "ld", "mod", "mot", "rack"]

for k in implemented_prefixes:
    for c in cmd_defs.cmd_list[k]:
        
        zeroed_params = [x if x != "" else "0" for x in c["params"]]
        sparse_params = [x for x in c["params"] if x != "" and x != "0" and x[0] not in "0123456789ABCDEF"]

        if c["header_only"]:
            c_src = f"""

def {c["fxn_name"]}({", ".join(sparse_params[1:])}):
    return struct.pack("{cmd_defs.header_only_struct}", {c["msg_id"]}, {", ".join(zeroed_params[1:])})

"""
            
        else:
            c_src = f"""

def {c["fxn_name"]}({", ".join(sparse_params[1:])}):
    data = struct.pack("{c["struct"]}", {", ".join(zeroed_params[4:])})
    header = struct.pack("{cmd_defs.header_data_struct}", {c["msg_id"]}, len(data), dst, src)
    return header + data

"""
        exec(c_src)
        setattr(pack_cmds, c["fxn_name"], globals()[c["fxn_name"]])