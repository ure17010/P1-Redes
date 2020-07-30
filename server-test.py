import socket
import select
import pickle

HEADER_LENGTH = 10 
IP = "127.0.0.1"
PORT = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#para permitir reconectar
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP,PORT))
server_socket.listen()
print(f"Server listening in {IP}:{PORT}")

sockets_list = [server_socket]

clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        
        message_length  = int(message_header.decode('utf-8').strip())
        data = pickle.loads(client_socket.recv(message_length))
        return {"header": message_header, "data": data}


    except:
        return False

def useraccepted(username):
    dprotocol = {
        'type': 'useraccepted',
        'username': username,
        'roomID': 1
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg

def broadcast(username,message):
    dprotocol = {
        'type': 'message',
        'username': username,
        'message': message
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg


while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:

        # cuando alguien se acaba de conectar al server
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()
            user = receive_message(client_socket)
            if user is False:
                continue
            if user['data']['type'] == 'signin':
                msg = useraccepted(user['data']['username'])
                # Sending useraccepted
                client_socket.send(msg)

                # Wait for singinok
                signinok = False
                while not signinok:
                    message = receive_message(client_socket)
                    if message is False:
                        continue
                    if message['data']['type'] == "signinok":
                        signinok = True

                sockets_list.append(client_socket)
                clients[client_socket] = user
                print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data']['username']}")

        else:
            message = receive_message(notified_socket)
            print(message)

            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data']['username']}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            
            if message['data']['type'] == 'sendmessage':
                print(f"Received message from {user['data']['username']}: {message['data']['message']}")
                msg = broadcast(user['data']['username'],message['data']['message'])
                for client_socket in clients:
                    # send message to every client except the sender
                    if client_socket != notified_socket:
                        client_socket.send(msg)
            else:
                print(f"El tipo de mensaje es: {message['data']['type']}")

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
