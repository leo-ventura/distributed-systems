from typing import List

import grpc
import server_pb2
import server_pb2_grpc
import node_pb2
import node_pb2_grpc


def print_help() -> None:
    print("Help")

def search(args: List[str]) -> None:
    id_busca: int = 0   # TODO change id_busca to something meaningful
    no_origem: int = int(args[0])
    chave: str = args[1]
    no_origem_port: int = 60000 + no_origem


    with grpc.insecure_channel(f'localhost:{no_origem_port}') as channel:
        node_stub: node_pb2_grpc.NodeStub = node_pb2_grpc.NodeStub(channel)
        node_response = node_stub.Lookup(node_pb2.LookupRequest(
            no_origem=no_origem,
            key=chave
        ))

    if node_response.value:
        print(f'[Cliente]: chave {chave} referenciando valor "{node_response.value}" encontrado no nó {node_response.node_id}')
    else:
        print(f'[Cliente]: chave {chave} não encontrada, deveria estar presente no nó {node_response.node_id}')


def insert(args: List[str]) -> None:
    no_origem: int = int(args[0])
    chave: str = args[1]
    valor: str = args[2]
    no_origem_port: int = 60000 + no_origem
    print(f'Insert:\n no: {no_origem}\n chave: {chave}\n valor: {valor}')
    print(f' porta: {no_origem_port}')

    with grpc.insecure_channel(f'localhost:{no_origem_port}') as channel:
        node_stub: node_pb2_grpc.NodeStub = node_pb2_grpc.NodeStub(channel)
        node_response = node_stub.Insert(node_pb2.InsertRequest(
            no_origem=no_origem,
            key=chave,
            value=valor
        ))

    print(f'[Cliente]: valor "{valor}" identificado pela chave "{chave}" foi inserido no nó {node_response.node_insert}')

def run() -> None:
    print_help()

    while True:
        cmd_input: str = input()
        cmd_split: List[str] = cmd_input.split()
        cmd: str = cmd_split[0]
        cmd_arguments: List[str] = cmd_split[1:]

        if cmd == 'search':
            search(cmd_arguments)
        elif cmd == 'insert':
            insert(cmd_arguments)
        elif cmd == 'end':
            break
        else:
            print(f'Comando {cmd} não reconhecido')

if __name__ == '__main__':
    run()