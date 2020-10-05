import logging

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock, Condition, current_thread

from chat import protocol
from chat.message.socket_reader import read_response
from chat.message.socket_reader import SocketClosedError
from chat.sockets_wrappers.listener_socket import ListenerSocket

import chat.message.builder as builder

class ServerSocket(ListenerSocket):
    def __init__(self, address, max_connections=5):
        super().__init__(address, max_connections)
        self._lock = Lock()
        self._can_read_response = Condition()
        self._threads = {}
        self._shared_data = ""

    def ready(self, open_clients, nicknames):
        # spawn new process to handle new client connection
        client = Thread(target=self._handle_new_client_connection, args=(nicknames,))
        client.start()

        open_clients.append(client)
        return False

    def _handle_new_client_connection(self, nicknames):
        """ Handles new connection from client """
        # accept new connections
        c_sock, addr = self._sock.accept()
        logging.info(f'Accepted connection from: {addr}')

        self._keep_alive(c_sock, nicknames)

        logging.info(f'Empty response from {addr} received, closing connection')

        # close client socket descriptor
        c_sock.close()

    def _keep_alive(self, c_sock, nicknames):
        # deal with information received from this connection
        while True:
            try:
                response = read_response(c_sock)
                logging.debug(f'Read response: {response}')
            except SocketClosedError:
                logging.debug(f'Socket {c_sock.getsockname()} has been closed')
                break

            # decode byte encoded response
            logging.debug(f'Client sent: {response}')

            self._handle_response(c_sock, nicknames, response)

    def _handle_response(self, c_sock, nicknames, response):
        if protocol.first_interaction in response:
            self._handle_first_interaction(c_sock, nicknames, response[protocol.nick])
        elif protocol.action_field in response:
            # user requested some type of action
            if protocol.action.LIST_CLIENTS_FIELD in response[protocol.action_field]:
                self._handle_list_clients(c_sock, nicknames)
            elif protocol.action.CONNECT_CLIENT_FIELD in response[protocol.action_field]:
                self._handle_new_p2p_conn(c_sock, nicknames, response[protocol.nick])
        elif protocol.connection.ip in response and protocol.connection.port in response:
            # p2p connection has been created
            # put data in the shared memory so that the main thread can pick it up
            with self._can_read_response:
                self._shared_data = response
                self._can_read_response.notify()

            # go back to the keep alive loop
            self._keep_alive(c_sock, nicknames)

    def _handle_list_clients(self, c_sock, nicknames):
        logging.info(f'Send active clients list')

        self._remove_inactive_clients(nicknames)

        payload = builder.build_list_clients_payload(nicknames)
        c_sock.sendall(payload)

    def _handle_new_p2p_conn(self, c_sock, nicknames, target_nickname):
        logging.info(f'[p2p] Creating new p2p connection to {target_nickname}')

        if target_nickname in nicknames:
            self._handle_active_client(c_sock, nicknames, target_nickname)
        else:
            logging.error(f'Nickname {target_nickname} is not active')
            self._handle_not_active_client(c_sock, target_nickname)

    def _handle_active_client(self, c_sock, nicknames, target_nickname):
        response = self._send_server_request_to_target(nicknames, target_nickname)
        self._send_target_info_to_client(c_sock, response)

    def _send_server_request_to_target(self, nicknames, target_nickname):
        # create payload asking target nickname to act as a server
        payload = builder.build_p2p_serve_request_payload(protocol.role.server)
        c_sock_p2p_server = nicknames[target_nickname]

        logging.debug(f'[p2p] Sending {payload} to {c_sock_p2p_server}')
        c_sock_p2p_server.sendall(payload)

        # join thread to wait until it receives the response
        response = self._read_response_from_shared_memory(target_nickname)
        logging.debug(f'[p2p] c_sock_p2p_server responded: {response}')
        return response

    def _send_target_info_to_client(self, c_sock, response):
        # forward ip and port to client of the p2p connection
        payload = builder.build_p2p_server_payload((
            response[protocol.connection.ip],
            response[protocol.connection.port]
        ))
        logging.debug(f'[p2p] Sending {payload} to {c_sock.getsockname()}')
        c_sock.sendall(payload)

    def _handle_not_active_client(self, c_sock, nickname):
        payload = builder.build_status_payload(nick=nickname, ok=False)

        c_sock.sendall(payload)

    def _read_response_from_shared_memory(self, nickname):
        logging.debug(f'Shared data before wait join: {self._shared_data}')
        with self._can_read_response:
            self._can_read_response.wait()

            logging.debug(f'Shared data after releasing join: {self._shared_data}')
            response = self._shared_data
            self._share_data = ""

        return response

    def _handle_first_interaction(self, c_sock, nicknames, nickname):
        logging.info(f'First interaction, got nickname: {nickname}')
        if nickname in nicknames:
            status_payload = builder.build_status_payload(nickname, ok=False)
        else:
            self._atomic_update_nickname(nicknames, nickname, c_sock)
            status_payload = builder.build_status_payload(nickname)

        logging.debug(f'Sending status payload: {status_payload}')
        c_sock.sendall(status_payload)

    def _atomic_update_nickname(self, nicknames, nickname, c_sock):
        with self._lock:
            logging.debug(f'Adding {nickname}')
            nicknames[nickname] = c_sock
            self._threads[nickname] = current_thread()

            logging.debug(f'Nicknames: {nicknames}')
            logging.debug(f'Threads: {self._threads}')

    def _remove_inactive_clients(self, nicknames):
        logging.debug(f'Threads: {self._threads.keys()}')
        for nickname in list(nicknames.keys()):
            if not self._threads[nickname].is_alive():
                logging.debug(f'Removing {nickname} from active clients')
                del nicknames[nickname]
