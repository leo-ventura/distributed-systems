from typing import List
from concurrent import futures
from multiprocessing import Process

from node import Node

import grpc

STARTING_PORT = 60000

def create_nodes(n: int) -> List[Process]:
    active_processes: List[Process] = []

    number_of_nodes: int = 2**n
    for node_id in range(number_of_nodes):
        port: int = STARTING_PORT + node_id

        process: Process = Process(target=Node, args=(number_of_nodes, node_id, port))
        process.start()
        active_processes.append(process)

    return active_processes

def init_chord_ring(n: int=10) -> None:
    """ Initialiaze chord ring with 2^n nodes """
    active_processes: List[Process] = create_nodes(n)

    while True:
        msg = input()
        if msg == 'out':
            break

def serve() -> None:
    n: int = read_n()
    init_chord_ring(n)

def read_n() -> int:
    n_input: str = input("n: ")
    try:
        n: int = int(n_input)
    except:
        n = read_n()
    finally:
        return n

if __name__ == '__main__':
    serve()