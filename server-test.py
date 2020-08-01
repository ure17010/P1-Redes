"""
Universidad del Valle de Guatemala 
Redes
CAtedrático: Vinicio Paz

Estuardo Ureta - Oliver Mazariegos - Pablo Viana

-> Un servidor en python que administre un juego de old maid
"""
import socket
import select
import pickle

#Variables globales
HEADER_LENGTH = 10 
IP = "127.0.0.1"
PORT = 5555
clients = {}

#Creamos los sockets para la conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#para permitir reconectar
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP,PORT))
server_socket.listen()

print(f"Server listening in {IP}:{PORT}")

#Una lista con todos los sockets
sockets_list = [server_socket]

def receive_message(client_socket):
    """Esta función deserializa el mensaje y lo regresa como un json"""
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
    """Función que acepta una nueva conexión como cliente en el server"""
    dprotocol = {
        'type': 'useraccepted',
        'username': username,
        'roomID': 1
    }
    
    return dprotocol

def send_message(client_socket,dprotocol):
    """Esta función sirve para mandar mensajes a clientes en específivo"""
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    print(msg)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    #print(msg)
    client_socket.send(msg)
 
def broadcast(username,message, roomID):
    """Esta función manda un mensaje a todos los que este en un mismo room ID"""
    dprotocol = {
        'type': 'message',
        'username': username,
        'message': message
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    #print(msg)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    #print(msg)
    for user in clients:
    # send message to every client except the sender
        if clients[user]['username'] != username and clients[user]['roomID'] == roomID:
            user.send(msg)


if __name__ == "__main__":
    try:
        #variable para controlar el while
        bandera = True
        while bandera:
            read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

            for notified_socket in read_sockets:
                # cuando alguien se acaba de conectar al server
                if notified_socket == server_socket:
                    client_socket, client_address = server_socket.accept()
                    #Recibimos primer mensaje del server
                    user = receive_message(client_socket)
                    if user is False:
                        continue
                    if user['data']['type'] == 'signin':
                        userdata = useraccepted(user['data']['username'])
                        send_message(client_socket, userdata)
                        # Wait for singinok
                        signinok = False
                        while not signinok:
                            message = receive_message(client_socket)
                            if message is False:
                                continue
                            if message['data']['type'] == "signinok":
                                signinok = True
                        # agregamos al usuario a la listas lista de control
                        sockets_list.append(client_socket)
                        clients[client_socket] = message['data']
                        print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username: {user['data']['username']}")

                else:
                    # recibimos mensaje del server
                    message = receive_message(notified_socket)

                    if message is False:
                        #Se cierra la conexión
                        print(f"Closed connection from {clients[notified_socket]['username']}")
                        sockets_list.remove(notified_socket)
                        del clients[notified_socket]
                        continue
                    #Identificamos al usuario del cual proviene el socket
                    user = clients[notified_socket]
                    
                    if message['data']['type'] == 'broadcast':
                        # si es para mandar un mensaje a todos los clientes
                        print(f"Received message from {user['username']}: {message['data']['message']}")
                        msg = broadcast(user['username'], message['data']['message'], user['roomID'])
                    else:
                        print("falta implementar")

                for notified_socket in exception_sockets:
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
        exit()
    except KeyboardInterrupt:
        print("hasta pronto")
        exit()