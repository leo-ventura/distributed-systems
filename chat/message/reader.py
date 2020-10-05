import json
import socket
import struct

def decode_size(size):
    """
        Decode the size of the payload, from network (big endian) to host
    [ref] https://docs.python.org/3/library/struct.html#byte-order-size-and-alignment
    """
    size_unpacked = struct.unpack("!I", size)[0]
    return size_unpacked

def decode_json(json_string):
    """ Read json string, convert to Python dictionary """
    return json.loads(json_string)
