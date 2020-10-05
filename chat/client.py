#!/bin/python3
import argparse
import logging
import sys

from select import select
from socket import socket, AF_INET, SOCK_STREAM

import pathlib
import sys
sys.path.append(pathlib.Path.cwd().parent.as_posix())

from chat.util import parse_arguments, setup_logging, colors, shell_print
from chat.sockets_wrappers.client_socket import ClientSocket
from chat.sockets_wrappers.client_stdin import ClientStdinWrapper

from chat import protocol


def print_commands():
    for command in protocol.commands:
        print(f'{command}:\t\t{protocol.commands[command]}')

def usage():
    print("Bem vindo ao Chat Distribuído v1.0")
    print("="*20)
    print("Primeiro, digite um nickname para ser identificado")
    print("Depois, utilize os comandos para se comunicar com o servidor:")
    print_commands()
    print("="*20)


def connect():
    setup_logging(logging.ERROR)
    address = parse_arguments()

    # print usage
    usage()

    sock = ClientSocket(address)

    # start first interaction,
    # handle nickname setup
    sock.first_interaction()

    # setup sockets
    stdin = ClientStdinWrapper()

    # input entries
    readers_descriptors = [sock, stdin]
    writers_descriptors = []
    exceptions_descriptors = []

    # open connetions
    open_connections = []

    while True:
        shell_print()
        # get descriptors ready for interaction
        readers_ready, _, _ = select(readers_descriptors, writers_descriptors,
            exceptions_descriptors)

        logging.debug(f'Descriptors ready for reading: {readers_ready}')
        for reader in readers_ready:
            connections_closed, command = reader.ready(open_connections)

        if connections_closed:
            break
        elif command:
            sock.send_command(open_connections, command)

    sock.close()

if __name__ == '__main__':
    connect()