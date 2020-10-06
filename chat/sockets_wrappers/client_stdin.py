import sys
import logging

class ClientStdinWrapper:
    def __init__(self, can_read):
        self._stdin = sys.stdin
        self._can_read = can_read

    def fileno(self):
        # only allow `select` to return when _can_read is set
        # by doing this, we can differentiate between writing a command
        # or a message
        self._can_read.wait()
        return self._stdin.fileno()

    def ready(self, open_connections):
        connections_closed = False
        msg = self._stdin.readline().strip()
        logging.debug(f'Read message from stdin: {msg}')
        if not msg:
            # close remaining connections
            for conn in open_connections:
                logging.debug(f'Waiting for open clients: {open_connections}')
                conn.join()

            connections_closed = True

            logging.info('All clients closed')

        return connections_closed, msg