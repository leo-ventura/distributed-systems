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
    setup_logging()
    listenerAddress = parse_arguments()

    # setup server socket
    sock = ServerSocket(listenerAddress)
    stdin = ServerStdinWrapper()

    # input entries
    readersDescriptors = [sock, stdin]
    writersDescriptors = []
    exceptionsDescriptors = []

    # clients created throughout the execution
    clients = []

    # dictionary mapping nicknames to client_socket
    nicknames = {}

    # keep socket descriptor open as long as it still receives new connections
    while True:
        # get descriptors ready for interaction
        readersReady, _, _ = select(readersDescriptors, writersDescriptors,
            exceptionsDescriptors)

        logging.debug(f'Descriptors ready for reading: {readersReady}')
        for reader in readersReady:
            clientsClosed = reader.ready(clients, nicknames)

        if clientsClosed:
            break

    # close server socket descriptor
    sock.close()

    logging.info('All connections closed, shutting down server')

if __name__ == '__main__':
    serve()