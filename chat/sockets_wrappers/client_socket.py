import logging

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from chat import protocol
from chat.util import colors, shell_print, print_message_chat, print_received_message, print_nicknames
from chat.message.socket_reader import read_response

from chat.sockets_wrappers.client_server_socket import ClientServerSocket

import chat.message.builder as builder

class ClientSocket:
    def __init__(self, address):
        self._nick = ""

        # create socket descriptor
        self._sock = socket(AF_INET, SOCK_STREAM)

        # connect to server
        self._sock.connect(address)

    def fileno(self):
        return self._sock.fileno()

    def close(self):
        self._sock.close()

    def ready(self, open_connections):
        # received connection from the server
        response = read_response(self._sock)
        if (protocol.role_field in response
            and response[protocol.role_field] == protocol.role.server):
            self._create_p2p_server(open_connections)
        else:
            logging.debug(f'Received request from the server, but request was: {response}')
        return False, ""

    def first_interaction(self):
        nickname_payload = setup_nickname()
        self._sock.sendall(nickname_payload)

        response = read_response(self._sock)
        if response[protocol.status.ok]:
            self._nick = response[protocol.nick]
            print(f"{colors.OKBLUE}Nickname criado com sucesso!{colors.ENDC}")
        else:
            print(f"{colors.FAIL}Nickname já existente, tente novamente{colors.ENDC}")
            self.first_interaction()

    def _create_p2p_server(self, open_connections):
        logging.debug(f'Creating p2p server')
        client_p2p_server = ClientServerSocket()

        connection = Thread(target=client_p2p_server.init_p2p_server)
        connection.start()

        self._return_to_server_p2p_address(client_p2p_server.get_address())

        open_connections.append(connection)

    def _return_to_server_p2p_address(self, p2p_address):
        p2p_server_payload = builder.build_p2p_server_payload(p2p_address)
        self._sock.sendall(p2p_server_payload)

    def send_command(self, open_connections, command):
        command_arguments = command.split()
        action = command_arguments[0]
        if action == protocol.action.LIST_CLIENTS:
            self._send_list_clients_request()
        elif action == protocol.action.CONNECT_CLIENT:
            nickname = command_arguments[1]
            self._send_connect_client_request(open_connections, nickname)
        else:
            print(f"{colors.FAIL}Comando inválido, tente novamente{colors.ENDC}")

    def _send_list_clients_request(self):
        payload = builder.build_action_payload(protocol.action.LIST_CLIENTS_FIELD)
        self._sock.sendall(payload)

        response = read_response(self._sock)
        active_clients = response[protocol.action.LIST_CLIENTS_FIELD]
        print("Active clients:")
        print_nicknames(active_clients)

    def _send_connect_client_request(self, open_connections, nickname):
        payload = builder.build_action_payload(protocol.action.CONNECT_CLIENT_FIELD,
            nickname)
        self._sock.sendall(payload)

        response = read_response(self._sock)

        self._create_p2p_client(open_connections, response)

    def _create_p2p_client(self, open_connections, response):
        address = (response[protocol.connection.ip], response[protocol.connection.port])

        client_p2p_socket = ClientSocket(address)

        connection = Thread(target=client_p2p_socket.interact_p2p)
        connection.start()

        open_connections.append(connection)

    def interact_p2p(self):
        # while True:
        # read user message
        print_message_chat()
        msg = input()
        # if not msg:
        #     TODO handle empty message on p2p chat
        #     return
        logging.debug(f"Sending {msg} from {self._nick}")

        payload = builder.build_message_payload(self._nick, msg)
        self._sock.sendall(payload)

        response = read_response(self._sock)
        print_received_message(response[protocol.nick], response[protocol.message])
        self.close()

def setup_nickname():
    nickname = get_user_nickname()
    return builder.build_nickname_payload(nickname)

def get_user_nickname():
    print("Entre com um nome de usuário para sua sessão atual no CD")
    shell_print()

    nickname = input()
    return nickname