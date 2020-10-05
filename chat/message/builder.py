import json
import socket
import struct

from chat import protocol

def encode_size(size):
    """ Encode the size of the payload from host to network (big endian) """
    return struct.pack("!I", size)

def encode_dict(json_dict):
    """ Encode dictionary to json string, then byte encode it """
    return json.dumps(json_dict).encode('utf-8')

def build_payload(json_dict):
    """ Build the payload by encoding the dictionary, encoding its size
    and then concatenating them to create the actual payload """
    byte_encoded_json = encode_dict(json_dict)
    size_payload = encode_size(len(byte_encoded_json))
    return size_payload + byte_encoded_json

def build_nickname_payload(nickname):
    nickname_dict = {
        protocol.first_interaction: True,
        protocol.nick: nickname
    }

    return build_payload(nickname_dict)

def build_action_payload(action, nickname=""):
    action_dict = {
        protocol.nick: nickname,
        protocol.action_field: action
    }

    return build_payload(action_dict)

def build_message_payload(nickname, message):
    message_dict = {
        protocol.nick: nickname,
        protocol.message: message
    }

    return build_payload(message_dict)

def build_p2p_server_payload(p2p_server_address):
    p2p_server_dict = {
        protocol.connection.ip: p2p_server_address[0],
        protocol.connection.port: p2p_server_address[1],
    }

    return build_payload(p2p_server_dict)

def build_p2p_serve_request_payload(role):
    p2p_serve_dict = {
        protocol.role_field: role
    }

    return build_payload(p2p_serve_dict)

def build_status_payload(nick='', ok=True):
    ok_dict = {
        protocol.status.ok: ok,
        protocol.nick: nick
    }

    return build_payload(ok_dict)

def build_list_clients_payload(nicknames):
    list_clients_dict = {
        protocol.action.LIST_CLIENTS_FIELD: [nick for nick in nicknames],
    }

    return build_payload(list_clients_dict)
