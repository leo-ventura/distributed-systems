class action:
    LIST_CLIENTS_FIELD = "list_clients"
    CONNECT_CLIENT_FIELD = "connect_client"
    LIST_CLIENTS = "l"
    CONNECT_CLIENT = "c"

class status:
    ok = "ok"

class connection:
    ip = "ip"
    port = "port"

class role:
    server = "server"
    client = "client"

class protocol:
    action = action
    status = status
    connection = connection
    role = role
    nick = "nick"
    message = "msg"
    role_field = "role"
    action_field = "action"
    first_interaction = "first_interaction"
    commands = {
        action.LIST_CLIENTS: "lista usuários ativos",
        action.CONNECT_CLIENT + " <nickname>": "pede servidor informações para conexão com o cliente <nickname>"
    }