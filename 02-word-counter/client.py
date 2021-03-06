#!/bin/python3
import argparse
import logging
import sys

from util import parseArguments
from socket import socket, AF_INET, SOCK_STREAM

def usage():
    print("Contador de palavras v1.0")
    print("="*20)
    print("Digite o nome dos arquivos que pretende contar as palavras")
    print("Separe o nome dos arquivos por espaço.")
    print("Exemplo: words.txt server.py")
    print("="*20)

def shellPrint():
    print("> ", end="", flush=True)

def connect():
    address = parseArguments()

    # create socket descriptor
    sock = socket(AF_INET, SOCK_STREAM)

    # connect to server
    sock.connect(address)

    # print usage
    usage()

    shellPrint()
    # keep reading until user presses CTRL + D
    for msg in sys.stdin:
        # remove trailing spaces
        msg = msg.strip()

        # byte encode message
        msg = msg.encode('utf-8')

        # send msg
        sock.send(msg)

        # receive response from server
        response = sock.recv(1024)

        # decode byte encoded message
        response = response.decode('utf-8')

        # print to the user
        print(response)
        shellPrint()

    sock.close()

if __name__ == '__main__':
    connect()