import logging

from socket import socket, AF_INET, SOCK_STREAM, MSG_WAITALL
from threading import Thread

from chat import protocol
from chat.util import colors, shell_print, print_message_chat, print_received_message, print_nicknames, print_colored
from chat.message.socket_reader import read_response, SocketClosedError

from chat.sockets_wrappers.client_server_socket import ClientServerSocket

import chat.message.builder as builder

class ClientSocket:
    """ Socket wrapper to act handle client interactions """
    def __init__(self, address, nickname=""):
        self._nick = nickname

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

        # should only receive connection from the server when other client
        # wishes to send a message
        # if that's the case, open a p2p server to handle future incoming connections
        if (protocol.role_field in response
            and response[protocol.role_field] == protocol.role.server):
            self._create_p2p_server(open_connections)
        else:
            logging.debug(f'Received unexpected request from the server: {response}')
        return False, ""

    def first_interaction(self):
        """ Handle first interaction with the user, get their desired nickname """
        try:
            nickname_payload = setup_nickname()
        except EOFError:
            # no nickname provided, close connection
            self.close()

        # send nickname payload
        self._sock.sendall(nickname_payload)

        self._handle_first_interaction_response()

    def _handle_first_interaction_response(self):
        try:
            response = read_response(self._sock)
        except SocketClosedError:
            print("Socket fechado, tente novamente")
        else:
            if response[protocol.status.ok]:
                logging.debug(f'Setting nickname as {response[protocol.nick]}')
                self._nick = response[protocol.nick]
                print_colored(colors.OKBLUE, "Nickname criado com sucesso!")
            else:
                print_colored(colors.FAIL, "Nickname já existente, tente novamente")
                self.first_interaction()

    def send_command(self, open_connections, command):
        """ User sent a command via stdin, forward it to the server """
        command_arguments = command.split()
        action = command_arguments[0]
        if action == protocol.action.LIST_CLIENTS:
            self._send_list_clients_request()
        elif action == protocol.action.CONNECT_CLIENT:
            try:
                nickname = command_arguments[1]
            except IndexError:
                print_colored(colors.WARNING, "Nenhum nickname fornecido, tente novamente")
            else:
                self._send_connect_client_request(open_connections, nickname)
        else:
            print_colored(colors.FAIL, "Comando inválido, tente novamente")

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

    def _send_list_clients_request(self):
        payload = builder.build_action_payload(protocol.action.LIST_CLIENTS_FIELD)
        self._sock.sendall(payload)

        response = read_response(self._sock)
        active_clients = response[protocol.action.LIST_CLIENTS_FIELD]
        print("Active clients:")
        print_nicknames(active_clients, self._nick)

    def _send_connect_client_request(self, open_connections, nickname):
        payload = builder.build_action_payload(protocol.action.CONNECT_CLIENT_FIELD,
            nickname)
        self._sock.sendall(payload)

        response = read_response(self._sock)

        self._create_p2p_client(open_connections, response)

    def _create_p2p_client(self, open_connections, response):
        address = (response[protocol.connection.ip], response[protocol.connection.port])

        client_p2p_socket = ClientSocket(address, nickname=self._nick)

        connection = Thread(target=client_p2p_socket.interact_p2p)
        connection.start()

        open_connections.append(connection)

    def interact_p2p(self):
        # while True:
        # read user message
        print_message_chat()
        msg = input()
        while not msg:
            error = "Não é possível enviar uma mensagem vazia, digite alguma coisa"
            print_colored(colors.WARNING, error)
            msg = input()

        logging.debug(f"Sending {msg} from {self._nick}")

        payload = builder.build_message_payload(self._nick, msg)
        self._sock.sendall(payload, MSG_WAITALL)

        shell_print()

        self.close()

def setup_nickname():
    nickname = get_user_nickname()
    return builder.build_nickname_payload(nickname)

def get_user_nickname():
    print_colored(colors.OKBLUE, "Entre com um nome de usuário para sua sessão atual")
    shell_print()

    nickname = input()
    return nickname