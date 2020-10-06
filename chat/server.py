#!/bin/python3
import argparse
import logging

import pathlib
import sys
sys.path.append(pathlib.Path.cwd().parent.as_posix())

from chat.util import parse_arguments, setup_logging
from chat.sockets_wrappers.server_stdin import ServerStdinWrapper
from chat.sockets_wrappers.server_socket import ServerSocket

from select import select

def serve():
    listenerAddress, debug = parse_arguments()
    setup_logging(debug=debug, level=logging.INFO)

    # setup server socket
    sock = ServerSocket(listenerAddress)
    stdin = ServerStdinWrapper()

    # input entries
    readers_descriptors = [sock, stdin]
    writers_descriptors = []
    exceptions_descriptors = []

    # clients created throughout the execution
    clients = []

    # dictionary mapping nicknames to client_socket
    nicknames = {}

    # keep socket descriptor open as long as it still receives new connections
    while True:
        # get descriptors ready for interaction
        readers_ready, _, _ = select(readers_descriptors, writers_descriptors,
            exceptions_descriptors)

        logging.debug(f'Descriptors ready for reading: {readers_ready}')
        for reader in readers_ready:
            clientsClosed = reader.ready(clients, nicknames)

        if clientsClosed:
            break

    # close server socket descriptor
    sock.close()

    logging.info('All connections closed, shutting down server')

if __name__ == '__main__':
    serve()