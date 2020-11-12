import argparse
import logging

class colors:
    red = '\033[91m'
    green = '\033[92m'
    yellow = '\033[93m'
    blue = '\033[94m'
    magenta = '\033[95m'
    cyan = '\033[96m'
    endc = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

def shell_print():
    print_colored(colors.cyan, "> ", end="")

def print_colored(color, string, end="\n"):
    print(f'{color}{string}{colors.endc}', end=end)
