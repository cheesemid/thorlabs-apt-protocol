from . import cmd_defs
import struct

# empty object
pack_cmds = type("", (), {})()

implemented_prefixes = [
    "hub",
    "hw",
    "kna",
    "kpz",
    "ksg",
    "la",
    "ld",
    "mod",
    "mot",
    "nt",
    "pz",
    "rack",
]


def pack_0x0453(chanident, dst, src, absolutedistance=None):
    # mot_move_absolute
    if absolutedistance is None:
        header = struct.pack(
            cmd_defs.header_only_struct, 0x0453, chanident, 0, dst, src
        )
        return header
    else:
        data = struct.pack("<Hl", chanident, absolutedistance)
        header = struct.pack(cmd_defs.header_data_struct, 0x0453, 6, dst, src)

        return header + data


for k in implemented_prefixes:
    for c in cmd_defs.cmd_list[k]:
        if c["has_subcmds"]:
            try:
                hex_msg_id = "0x" + c["msg_id"].to_bytes(2, "big").hex().upper()
                fxn = globals()[f"pack_{hex_msg_id}"]
                setattr(pack_cmds, c["fxn_name"], fxn)
                continue
            except KeyError as e:
                # some commands with subcommands are not implemented
                pass

        zeroed_params = [x if x != "" else "0" for x in c["params"]]
        sparse_params = [
            x
            for x in c["params"]
            if x != "" and x != "0" and x[0] not in "0123456789ABCDEF"
        ]

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
