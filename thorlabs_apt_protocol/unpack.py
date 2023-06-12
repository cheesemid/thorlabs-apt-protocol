from typing import Dict, Any
import struct
from . import cmd_defs

def unpack(data: bytes) -> Dict[str, Any]:
    header = data[:6]

    msg_id, _, dst, src = struct.unpack_from(cmd_defs.header_data_struct, header)

    c = cmd_defs.id_to_cmd[msg_id]

    sparse_params = [x for x in c["params"] if x != "" and x != "0" and x[0] not in "0123456789ABCDEF"]

    if c["header_only"]:
        unpacked = struct.unpack_from(cmd_defs.header_only_struct, data)
        
        ret = dict(zip(sparse_params, unpacked))
        ret["fxn_name"] = c["fxn_name"]

        return ret
    
    else:
        unpacked_header = struct.unpack_from(cmd_defs.header_data_struct, data)
        unpacked = struct.unpack_from(c["struct"], data[6:])

        ret = dict(zip(sparse_params, unpacked_header + unpacked))
        ret["fxn_name"] = c["fxn_name"]

        return ret
    
