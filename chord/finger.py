from typing import Tuple

from node_pb2_grpc import NodeStub

import grpc

class Finger:
    def __init__(self,
                start: int=0,
                interval: Tuple[int, int]=(0,0),
                node_id: int=0,
                port: int=0
            ) -> None:
        self.start: int = start
        self.interval: Tuple[int, int] = interval
        self.node_id: int = node_id
        self.port: int = port
        self.create_stub()

    def create_stub(self) -> None:
        channel: grpc.Channel = grpc.insecure_channel(f'localhost:{self.port}')
        self.stub: NodeStub = NodeStub(channel)

    def __repr__(self) -> str:
        return f'start: {self.start}\n' \
            f'interval: {self.interval}\n' \
            f'node_id: {self.node_id}\n'