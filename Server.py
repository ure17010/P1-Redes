"""
import socket
from _thread import *
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #conexion socket

#server y puerto definido
server = 'localhost'
port = 5555

server_ip = socket.gethostbyname(server)

#unir server con el puerto
try:
    s.bind((server, port))

#mensaje de fallo
except socket.error as e:
    print(str(e))

#busca conexiones al server
s.listen(3) #tres jugadores maximo
print("Waiting for a connection")

#tras tener ya una conexion de 3

IdActual = "0"

#espacio para funcion con ID (para cada usuario) y !!!NOT SURE!!!!



#para que mantenga reciviendo las diferentes conexiones
while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)

    start_new_thread(threaded_client, (conn,))
"""

"""
Universidad del Valle de Guatemala
Redes 
Catedrático: Vinicio 
Pablo Viana - Estuardo Ureta - Oliver Mazariegos 

Proyecto 1: juego de cartas ¿ya no es sequence?
"""

import socket, threading
class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        print ("New connection added: ", clientAddress)
    def run(self):
        print ("Connection from : ", clientAddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode()
            if msg=='bye':
              break
            print ("from client", msg)
            self.csocket.send(bytes(msg,'UTF-8'))
        print ("Client at ", clientAddress , " disconnected...")
        
LOCALHOST = "127.0.0.1"
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((LOCALHOST, PORT))
print("Server started")
print("Waiting for client request..")
while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()