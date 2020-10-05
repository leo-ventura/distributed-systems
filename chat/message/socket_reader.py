import json
import socket
import struct
import logging

from chat.message.reader import decode_json, decode_size

class SocketClosedError(Exception):
    """ Custom error to raise when a socket is closed """
    pass

def read_response(sock):
    """ Function responsible for reading the response of a specified socket """

    # first 4 bytes will always be the size of the payload to be read
    logging.debug('Waiting sock.recv(4)')
    payload_size = sock.recv(4)

    try:
        # decode how many bytes we need to read
        # converting from network ordering to host ordering
        bytes_to_read = decode_size(payload_size)
        logging.debug(f'Bytes to read: {bytes_to_read}')
    except struct.error:
        raise SocketClosedError

    # build json string
    json_string = ""
    while bytes_to_read > 0:
        response = sock.recv(min(bytes_to_read, 4096))
        if not response:
            raise SocketClosedError

        json_string += response.decode('utf-8')

        bytes_to_read -= len(response)

    logging.debug(f'JSON string: {json_string}')

    return decode_json(json_string)
