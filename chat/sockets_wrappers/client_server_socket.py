import logging

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from chat import protocol
from chat.util import print_received_message
from chat.message.socket_reader import read_response
from chat.sockets_wrappers.listener_socket import ListenerSocket

class ClientServerSocket(ListenerSocket):
    """ Socket wrapper to handle when a client needs to act as a server
        in a peer-to-peer interaction
    """
    def init_p2p_server(self):
        """ Initialize p2p server interaction by accepting a connection
            and reading its response.
            Does *not* send any data back.
        """
        c_sock, addr = self._sock.accept()
        logging.debug(f'Connection accepted from: {addr}')

        # receive message from the connected client
        response = read_response(c_sock)

        # and print it
        print_received_message(response[protocol.nick], response[protocol.message])

        # close both the client socket and itself
        c_sock.close()
        self.close()
