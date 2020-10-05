import argparse
import logging

class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    CYAN = '\033[96m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

LOG_FORMAT = "[%(asctime)s | %(levelname)s]: %(message)s"

def shell_print():
    print("> ", end="", flush=True)

def print_message_chat():
    print(f"{colors.CYAN}[Você] #>{colors.ENDC}", end="", flush=True)

def print_received_message(nickname, message):
    print(f'{colors.OKBLUE}[@{nickname}]: {message}{colors.ENDC}')
    shell_print()

def print_colored(color, string):
    print(f'{color}{string}{colors.ENDC}')

def print_nicknames(nicknames, self_nickname=""):
    if nicknames:
        index = 1
        for nickname in nicknames:
            formatted_output = f'[{index}]: @{nickname}'
            if nickname == self_nickname:
                print_colored(colors.CYAN, formatted_output)
            else:
                print(formatted_output)
            index += 1
    else:
        print(f"{colors.WARNING}Nenhum usuário ativo{colors.ENDC}")

def setup_logging(level=logging.DEBUG):
    logging.basicConfig(format=LOG_FORMAT, level=level)

def parse_arguments():
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
