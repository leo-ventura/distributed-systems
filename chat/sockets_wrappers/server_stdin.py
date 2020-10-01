import sys
import logging

from chat import protocol
from chat.util import print_nicknames

class ServerStdinWrapper:
    def __init__(self):
        self._stdin = sys.stdin

    def fileno(self):
        return self._stdin.fileno()

    def ready(self, open_connections, nicknames):
        """ Handles stdin entry """
        connections_closed = False
        msg = self._stdin.readline()
        msg = msg.strip()
        logging.debug(f'Read message from stdin: {msg}')
        if not msg:
            logging.debug(f'Waiting for open clients: {open_connections}')

            # close remaining connections
            for conn in open_connections:
                conn.join()

            logging.info('All clients closed')
            connections_closed = True
        elif msg == protocol.action.LIST_CLIENTS:
            print_nicknames(nicknames)

        return connections_closed
