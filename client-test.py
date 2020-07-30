import socket
import select
import errno
import sys
import pickle

HEADER_LENGTH = 10 
IP = "127.0.0.1"
PORT = 5555

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

def sendmessage(message):
    dprotocol = {
        "type":"sendmessage",
        "message": message
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg


# make conncection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)
print(f"Connected to server in {IP}:{PORT}")
signedin = False

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




while True:
    message = input(f"{my_username} > ")


    if message:
        msg = sendmessage(message)
        client_socket.send(msg)

    try:
        while True:
            # receive things
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                print("Connection closed by the server")
                sys.exit()

            msg = receive_message(client_socket,username_header)
            username = msg['data']['username']
            message = msg['data']['message']

            print(f"{username} > {message}")

    except IOError as e:
        # errores de lectura
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error',str(e))
            sys.exit()
        continue


    except Exception as e:
        print('General error', str(e))
        sys.exit()