import socket
import select
import errno
import sys
import pickle

HEADER_LENGTH = 10 
IP = "127.0.0.1"
PORT = 5555

# make conncection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)
print(f"Connected to server in {IP}:{PORT}")
my_username = input("Username: ")
dprotocol = {
    'type': 'signin',
    'username': my_username
}
# serializing dprotocol
msg = pickle.dumps(dprotocol)
# adding header to msg
msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
client_socket.send(msg)

def receive_message(client_socket,header = ''):
    try:
        if header == '': 
            message_header = client_socket.recv(HEADER_LENGTH)
        else:
            message_header = header
        if not len(message_header):
            return False
        
        message_length  = int(message_header.decode('utf-8').strip())
        data = pickle.loads(client_socket.recv(message_length))
        msg = {"header": message_header, "data": data}
        return {"header": message_header, "data": data}


    except:
        return False


def signinok(roomID):
    dprotocol = {
        "type":"signinok",
        "roomID": roomID
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg

def sendmessage(msgtype, message):
    dprotocol = {
        "type":msgtype,
        "message": message
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg

def menu():
    """ Funcion que se encarga del menu del cliente """

    #os.system('clear')  NOTA para windows tienes que cambiar clear por cls
    print ("Selecciona una opción")
    print ("\t1 - mandar mensaje")
    print ("\t2 - revisar la sala de chat")
    print ("\t3 - salir")

def writing_to_chat():
    """ Funcion para mandar un mensaje a todos en el room <-? """
    try:
        message = input("¿cúal es el mensaje? ")
        msg = sendmessage("broadcast", message)
        client_socket.send(msg)
        return True
    except:
        return False

def see_chat_room():
    """Funcion para ver mensajes que llegan de otros clientes """
    try:
        username_header = client_socket.recv(HEADER_LENGTH)
        if not len(username_header):
            print("Connection closed by the server")
            sys.exit()

        msg = receive_message(client_socket,username_header)
        username = msg['data']['username']
        message = msg['data']['message']

        print(f"{username} > {message}")

        return True
    except:
        return False

def quit_server():
    """Funcion especial para apagar servidor desde cliente"""
    try:
        msg = sendmessage("quit_server", "")
        client_socket.send(msg)
        return True
    except:
        return False

def client_on():
    signedin = False
    client_on = True
    while not signedin:
        try:
            while True:
                #wait for useraccepted
                message = receive_message(client_socket)
                if message:
                    if message['data']['username'] == my_username:
                        # send signinok
                        print(f"Singned in server @{IP}:{PORT} as {my_username}")
                        msg = signinok(message['data']['roomID'])
                        client_socket.send(msg)
                        signedin = True
                        break
                    else:
                        print(f"Server thought you were {message['data']['username']}")
                        print("Disconnecting...")
                        sys.exit()

        except IOError as e:
            # errores de lectura
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error',str(e))
                sys.exit()
            continue

        except Exception as e:
            print('General error', str(e))
            sys.exit()

    while client_on:
        menu()
        flag = True
        while flag:
            try:
                optmenu = int(input(f"{my_username} > "))
                if(optmenu > 3):
                    print("Ingresa un numero del menu")
                    menu()
                else:
                    flag = False
            except:
                print("ingrese una opcion valida")
                menu()

        if optmenu == 1:
            if not writing_to_chat():
                print("Trouble in writting room")
        elif optmenu == 2:
            if not see_chat_room():
                print("No messages")
        elif optmenu == 3:
            print("Hasta pronto")
            client_on = False
        #1001 - codigo especial para apagar el server desde el cliente por si se traba
        elif optmenu == 1001:
            if not quit_server():
                print("Trouble quitting the server")
    exit()

if __name__ == "__main__":
    try:
        client_on()
    except KeyboardInterrupt:
        pass