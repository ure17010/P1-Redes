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