import argparse
import logging

from socket import socket, AF_INET, SOCK_STREAM

LOG_FORMAT = "[%(asctime)s | %(levelname)s]: %(message)s"

def setupLogging():
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

def parseArguments():
    parser = argparse.ArgumentParser(
        description='Basic echo server implementation')
    parser.add_argument('--host', type=str, default='localhost',
                        help='Host', dest='host')
    parser.add_argument('-P', '--port', type=int, default=5000,
                        help='Port', dest='port')

    args = parser.parse_args()
    host = args.host
    port = args.port

    return host, port

def main():
    setupLogging()
    listenerAddress = parseArguments()

    # set up socket descriptor
    sock = socket(AF_INET, SOCK_STREAM)

    # bind connection to host and port given as parameters
    logging.debug(f'Binding connection on: {listenerAddress}')
    sock.bind(listenerAddress)

    # set up listener for new connections, max of 1 simultaneous connection
    logging.info('Listening...')
    sock.listen(1)

    # accept new connections
    cSock, addr = sock.accept()
    logging.info(f'Accepted connection from: {addr}')

    # deal with information received from this connection
    while True:
        response = cSock.recv(1024)

        # empty response
        if not response:
            logging.info('Empty response received, closing connection')
            break

        logging.debug(f'Client sent: {response}')

        # echo it back to the client
        cSock.send(response)

    # close client socket descriptor
    cSock.close()

    # close server socket descriptor
    sock.close()

    logging.info('All connections closed, shutting down server')

if __name__ == '__main__':
    main()