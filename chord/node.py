from concurrent import futures
import hashlib

from typing import List, Dict, Any

from finger import Finger
from node_pb2_grpc import NodeServicer, add_NodeServicer_to_server

import math
import grpc
import node_pb2
import node_pb2_grpc
import client_pb2
import client_pb2_grpc

HASH_SIZE = 160

class Node(NodeServicer):
    """
        Class representing a Node in the Chord ring
    """
    def __init__(self, n: int, node_id: int, port: int) -> None:
        print(f'Criando nó com node_id: {node_id}')
        self.n: int = n
        self.node_id: int = node_id
        self.port: int = port

        # self.successor_id is a node_id in the chord ring
        self.successor_id: int = (node_id + 1) % self.n
        self.predecessor_id: int = (node_id - 1) % self.n

        # each entry (node_id + 2^i mod 2^n) points to a stub, reversely ordered
        self.finger_table: Dict[int, Finger] = {}

        # actual table of current node
        self.hash_table: Dict[str, str] = {}

        self.init_finger_table()
        self.init_rpc_server()

    """ Methods to handle gRPC """
    def Lookup(self, request, context) -> node_pb2.Empty:
        """ RPC lookup """
        print(f'Passando pelo nó {self.node_id}')
        key: str = request.key
        hash_: int = self.hash_key(key)

        if self.is_id_at_current_node(hash_):
            try:
                value: str = self.hash_table[key]
            except KeyError:
                value = ""
            finally:
                with grpc.insecure_channel(f'localhost:{request.client_port}') as channel:
                    client_stub: client_pb2_grpc.ClientStub = client_pb2_grpc.ClientStub(channel)
                    _ = client_stub.ClientLookupReply(node_pb2.LookupReply(
                        node_id=self.node_id,
                        key=key,
                        value=value
                    ))
                    return node_pb2.Empty()

        finger_index: int = self.closest_preceding_finger(hash_)
        stub: node_pb2_grpc.NodeStub = self.finger_table[finger_index].stub
        return stub.Lookup(request)

    def Insert(self, request, context) -> node_pb2.Empty:
        """ RPC Insert """
        print(f'Passando pelo nó {self.node_id}')
        key: str = request.key
        hash_: int = self.hash_key(key)

        if self.is_id_at_current_node(hash_):
            value: str = request.value
            print(f'Inserindo valor "{value}" identificado pela chave "{key}", com hash {hash_}, no nó {self.node_id}')
            self.hash_table[key] = value

            with grpc.insecure_channel(f'localhost:{request.client_port}') as channel:
                client_stub: client_pb2_grpc.ClientStub = client_pb2_grpc.ClientStub(channel)
                _ = client_stub.ClientInsertReply(node_pb2.InsertReply(
                    node_insert=self.node_id,
                    key=key,
                    value=value
                ))

                return node_pb2.Empty()

        print(f'Procurando pela hash {hash_}')
        print(f'Finger table: {list(self.finger_table)}')
        finger_index: int = self.closest_preceding_finger(hash_)
        stub: node_pb2_grpc.NodeStub = self.finger_table[finger_index].stub
        return stub.Insert(request)

    def init_rpc_server(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        add_NodeServicer_to_server(self, server)
        server.add_insecure_port(f'localhost:{self.port}')
        server.start()
        server.wait_for_termination()

    """ Methods for the usual Chord implementation """
    def init_finger_table(self) -> None:
        for i in range(self.n.bit_length() - 1):
            finger_entry: int = (self.node_id + 2**i) % self.n

            successor_id: int = finger_entry + 1
            finger_port: int = (self.port - self.node_id + finger_entry)
            finger: Finger = Finger(
                start=finger_entry,
                interval=(finger_entry, finger_entry + 1),
                node_id=successor_id,
                port=finger_port
            )
            self.finger_table[finger_entry] = finger

    def closest_preceding_finger(self, hash_: int) -> int:
        for key in reversed(self.finger_table):
            if self.node_id < key and key <= hash_ \
            or key <= hash_ and hash_ < self.node_id:
                return key
        return self.node_id

    def is_id_at_current_node(self, id_: int) -> bool:
        return self.predecessor_id < id_ and id_ <= self.node_id

    def is_id_at_successor_node(self, id_: int) -> bool:
        return self.node_id < id_ and id_ <= self.successor_id

    def hash_key(self, id_: str) -> int:
        hashed_key: str = hashlib.sha1(id_.encode('utf-8')).hexdigest()
        return int(hashed_key, 16) % self.n
