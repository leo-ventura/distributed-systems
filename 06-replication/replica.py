from concurrent import futures
from threading import Thread, Event

from typing import List, Dict, NamedTuple
from util import print_colored, shell_print, colors

import grpc
import replica_pb2 as rep
import replica_pb2_grpc as rep_grpc

NUMBER_OF_NODES = 4
STARTING_PORT = 50000
SECONDS_TO_WAIT_RPC_METHODS_FINISH = 1

class HistoryEntry(NamedTuple):
    """ An entry in the history of changes

    Attributes:
        node_id: represents the id of the node that made the change
        value: new value of variable X
    """
    node_id: int
    value: int

class Stub(NamedTuple):
    """ A stub entry

    Attributes:
        node_id: represents the id of the node referenced by the stub
        stub: the actual stub used to communicate with the other node
    """
    node_id: int
    stub: rep_grpc.ReplicaStub


class Replica(rep_grpc.ReplicaServicer):
    def __init__(self, node_id: int) -> None:
        self.node_id: int = node_id
        self.port: int = STARTING_PORT + node_id
        self.X: int = 0
        self.history: List[HistoryEntry] = []
        self.is_primary: bool = node_id == 1
        self.init_replicas()
        self.init_server()
        print_help()

    # RPC methods
    def RequestHat(self, request, context):
        """ Handle hat request """
        message = rep.HatReply(
            node=self.node_id,
            was_primary=self.is_primary
        )

        self.commit()

        self.is_primary = False
        return message

    def UpdateCopy(self, request, context):
        """ Update variable x and history of changes """
        self.X = request.x
        self.insert_history_record(request.node, request.x)

        return rep.UpdateCopyReply(node=self.node_id)

    def run(self):
        """ Main method, initialize server interaction """

        while True:
            cmd, args = self.read_command()

            if cmd == 'help':
                print_help()
            elif cmd == 'w':
                self.set_x(args)
            elif cmd == 'r':
                self.read_x()
            elif cmd == 'c':
                self.commit()
            elif cmd == 'h':
                self.read_history()
            elif cmd == 'stop':
                break

        self.shutdown_server()

    # User requested commands
    def read_x(self):
        """ Read value x on current copy """
        print_colored(colors.green, f'X = {self.X}')

    def read_history(self):
        """ Read history of changes of variable x """
        print_colored(colors.blue, "Histórico de mudanças")
        for entry in self.history:
            node_id, value = entry
            print_colored(colors.magenta, f'{node_id}: {value}')

    def set_x(self, args: List[str]):
        """ Write `value` to x """
        try:
            x: int = int(args[0])
        except ValueError:
            warning = f"Não foi possível converter argumento {x} para inteiro"
            print_colored(colors.red, warning)

        else:

            if not self.is_primary:
                self.get_hat()

            self.X = x
            self.insert_history_record(self.node_id, x)

    def get_hat(self) -> None:
        for replica in self.replicas:
            try:
                response = replica.stub.RequestHat(
                    rep.HatRequest(node=self.node_id))
            except grpc._channel._InactiveRpcError:
                print_colored(colors.red, f'Servidor {replica.node_id} está inativo')
            else:
                if response.was_primary:
                    warning: str = f'Chapéu passado de servidor {response.node} para {self.node_id}'
                    print_colored(colors.red, warning)
                    self.is_primary = True
                    break
                else:
                    print(f'response: {response}')

    def commit(self):
        """ Replicate current value of x to other copies """
        if self.is_primary:
            for replica in self.replicas:
                try:
                    response = replica.stub.UpdateCopy(rep.UpdateCopyRequest(
                        node=self.node_id,
                        x=self.X
                    ))
                except grpc._channel._InactiveRpcError:
                    print_colored(colors.red, f'Servidor {replica.node_id} está inativo')
                else:
                    message: str = f'Servidor {response.node} reconheceu o commit'
                    print_colored(colors.green, message)

    def insert_history_record(self, node_id, value) -> None:
        self.history.append(
            HistoryEntry(
                node_id=node_id,
                value=value
            ))

    def read_command(self):
        """ Read command and returns command and arguments """
        shell_print()
        cmd: str = ""
        args: List[str] = []
        try:
            command: List[str] = input().split()
        except EOFError:
            print_colored(colors.yellow, "ctrl-d recebido, terminando servidor...")
            cmd = "stop"
        else:
            cmd = command[0].strip()
            args = command[1:]
        return cmd, args


    def init_replicas(self):
        """ Initialize stubs to other servers """
        self.replicas: List[Stub] = []

        # TODO use generator instead of iterating the list 2*n + (n-1) times
        nodes_ids = list(range(1, NUMBER_OF_NODES + 1))
        nodes_ids.remove(self.node_id)

        for node_id in nodes_ids:
            port: int = STARTING_PORT + node_id
            channel: grpc.Channel = grpc.insecure_channel(f'localhost:{port}')
            stub: rep_grpc.ReplicaStub = rep_grpc.ReplicaStub(channel)
            self.replicas.append(Stub(node_id=node_id, stub=stub))

    def init_server(self) -> None:
        self.stop = Event()
        thread = Thread(target=self.init_rpc_server)
        thread.start()

    def init_rpc_server(self) -> None:
        """ Initialize RPC server """
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        rep_grpc.add_ReplicaServicer_to_server(self, server)
        server.add_insecure_port(f'localhost:{self.port}')
        server.start()
        self.stop.wait()
        server.stop(SECONDS_TO_WAIT_RPC_METHODS_FINISH)

    def shutdown_server(self) -> None:
        """ Set Event variable in order to let RPC server stop """
        self.stop.set()


def print_help():
    print_colored(colors.blue, "Protocolo de replicação primária com cópia local")
    print_colored(colors.blue, "="*20)
    print_colored(colors.blue, "Comandos disponíveis:")
    print_colored(colors.green, "\t help:    printa essa ajuda")
    print_colored(colors.green, "\t w <x>:   escreve o valor <x> na varíavel X")
    print_colored(colors.green, "\t r:       lê o valor da varíavel X na cópia")
    print_colored(colors.green, "\t h:       printa histórico de mudanças na cópia")

def read_node_id():
    node:str = input("Entre o id do servidor atual: ")
    try:
        node_id: int = int(node)
    except ValueError:
        node_id = read_node_id()
    finally:
        return node_id

def main() -> None:
    node_id: int = read_node_id()
    replica: Replica = Replica(node_id)
    replica.run()

if __name__ == '__main__':
    main()