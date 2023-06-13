from typing import Dict, Any, Union
import struct
from . import cmd_defs


def unpack(data: bytes, return_bytes=False) -> Union[Dict[str, Any], None]:
    if len(data) < cmd_defs.header_size:
        return None

    header = data[: cmd_defs.header_size]

    msg_id, _, dst, src = struct.unpack_from(cmd_defs.header_data_struct, header)

    c = cmd_defs.id_to_cmd[msg_id]

    if c["header_only"]:
        unpacked_header = struct.unpack_from(cmd_defs.header_only_struct, data)

        ret = dict(zip(c["params"], unpacked_header))

        ret["fxn_name"] = c["fxn_name"]

    else:
        unpacked_header = struct.unpack_from(cmd_defs.header_data_struct, data)
        unpacked_data = struct.unpack_from(c["struct"], data[cmd_defs.header_size :])

        ret = dict(zip(c["params"], unpacked_header + unpacked_data))
        ret["fxn_name"] = c["fxn_name"]

    key_list = list(ret.keys())
    for k in key_list:
        if k == "" or k.startswith("0") or k == "_":
            ret.pop(k)

    if return_bytes:
        return (ret, data[: cmd_defs.header_size + struct.calcsize(c["struct"])])

    return ret


def unpack_stream(com, return_bytes=False):
    while True:
        header = b""

        while True:
            header += com.read(cmd_defs.header_size - len(header))

            if len(header) >= cmd_defs.header_size:
                break

        msg_id, _, dst, src = struct.unpack_from(cmd_defs.header_data_struct, header)

        c = cmd_defs.id_to_cmd[msg_id]

        data = b""

        if c["header_only"]:
            unpacked_header = struct.unpack_from(cmd_defs.header_only_struct, header)
            ret = dict(zip(c["params"], unpacked_header))
            ret["fxn_name"] = c["fxn_name"]
        else:
            unpacked_header = struct.unpack_from(cmd_defs.header_data_struct, header)
            data = com.read(struct.calcsize(c["struct"]))
            unpacked_data = struct.unpack_from(c["struct"], data)

            ret = dict(zip(c["params"], unpacked_header + unpacked_data))
            ret["fxn_name"] = c["fxn_name"]

        key_list = list(ret.keys())
        for k in key_list:
            if k == "" or k.startswith("0") or k == "_":
                ret.pop(k)

        if return_bytes:
            yield (ret, header + data)
        else:
            yield ret
