import logging

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

class ListenerSocket:
    def __init__(self, address=('', 0), max_connections=5):
        """ Binding to port 0 leaves to the SO to choose a random port for us """
        self._sock = self._initSocket(address, max_connections)

    def fileno(self):
        return self._sock.fileno()

    def close(self):
        self._sock.close()

    def get_address(self):
        return self._sock.getsockname()

    def _initSocket(self, address, max_connections):
        # set up socket descriptor
        sock = socket(AF_INET, SOCK_STREAM)

        # bind connection to host and port given as parameters
        logging.info(f'Binding connection on: {address}')
        sock.bind(address)

        # set up listener for new connections, max of max_connections simultaneous connection
        logging.info(f'Listening on {sock.getsockname()}...')
        sock.listen(max_connections)

        # sock.setblocking(False)
        # set timeout to 30 seconds
        # sock.settimeout(30)
        return sock
