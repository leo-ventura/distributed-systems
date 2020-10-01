import json
import socket
import struct

def decode_size(size):
    size_unpacked = struct.unpack("!I", size)[0]
    return size_unpacked
    # return socket.ntohl(size_unpacked)

def decode_json(json_string):
    return json.loads(json_string)
