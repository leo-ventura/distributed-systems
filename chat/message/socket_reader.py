import json
import socket
import struct
import logging

from chat.message.reader import decode_json, decode_size

class SocketClosedError(Exception):
    pass

def read_response(sock):
    logging.debug(f'Reading response using {sock.getsockname()}')
    # first 4 bytes will always be the size of the payload to be read
    try:
        logging.debug('Waiting at sock.recv(4)')
        payload_size = sock.recv(4)
        logging.debug(f'Payload size: {payload_size}')
        bytes_to_read = decode_size(payload_size)
        logging.debug(f'Bytes to read: {bytes_to_read}')
    except struct.error:
        raise SocketClosedError

    logging.debug(f'Finished reading bytes response, reading JSON')

    json_string = ""
    while bytes_to_read > 0:
        response = sock.recv(min(bytes_to_read, 4096))
        logging.debug(f'response = sock.recv(): {response}')
        if not response:
            raise SocketClosedError

        json_string += response.decode('utf-8')

        bytes_to_read -= len(response)

    logging.debug(f'JSON string: {json_string}')

    return decode_json(json_string)
