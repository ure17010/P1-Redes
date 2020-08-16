# importamos librerias
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import font 
import socket
import select
import errno
import sys
import pickle
import threading
import time

# variables globales
HEADER_LENGTH = 10 
IP = "127.0.0.1"
PORT = 5555
breakmech = False
flag_room = False
not_enough_players = True

lock = threading.RLock()
#un lock para cada variable ¿? no sé 
game_lock = threading.RLock()

# make conncection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)
print(f"Connected to server in {IP}:{PORT}")

class GUI(object):
    def __init__(self):
        pass

    def main_frame(self, root):
        #Frame Login
        root.title("Ingreso Cliente")
        root.resizable(width = False, height = False)
        root.configure(width = 500, height = 400)
        #Labeles login
        pls = Label(root, text = "Porfavor ingresa tu usuario y el # de opción  para continuar", justify = CENTER, font = "Helvetica 10 bold") 
        pls.place(relheight = 0.15, relx = 0.1, rely = 0.07)
        labelName = Label(root, text = "Usuario: ", font = "Helvetica 12") 
        labelName.place(relheight = 0.2, relx = 0.1, rely = 0.2)
        #Lables opciones Menu
        opcion1 = Label(root, text="1. Mandar mensaje", justify = CENTER, font = "Helvetica 8 bold")
        opcion1.place(relheight = 0.15, relx = 0.2, rely = 0.55)
        opcion2 = Label(root, text="2. Jugar", justify = CENTER, font = "Helvetica 8 bold")
        opcion2.place(relheight = 0.15, relx = 0.2, rely = 0.65)
        opcion9 = Label(root, text="9. Salir", justify = CENTER, font = "Helvetica 8 bold")
        opcion9.place(relheight = 0.15, relx = 0.2, rely = 0.75)
        #caja para escribir ususario
        self.my_username = StringVar() #variable para guardar el nombre
        self.entNombre = Entry(root, textvariable = self.my_username)
        self.entNombre.place(relwidth = 0.4,  relheight = 0.12, relx = 0.35, rely = 0.2)
        self.entNombre.focus()
        #caja para escribir opcion
        self.optmenu = int() #int para guardar la opcion
        self.entMenu = Entry(root, textvariable = self.optmenu)
        self.entMenu.place(relwidth = 0.15, relheight=0.12, relx = 0.80, rely=0.60)
        self.entMenu.focus()
        #bottones
        registro = Button(root, text = "Registrar Usuario",
                                    font="Helvetica 14 bold", 
                                    command = lambda: self.registro(self.entNombre.get()))
        registro.place(relx=0.4, rely=0.35)
        opciones = Button(root,text= "Elegir opción: ",
                                font="Helvetica 14 bold",
                                command = lambda: self.guardaroption(self.entMenu.get()))
        opciones.place(relheight = 0.15, relx = 0.45, rely = 0.60)
        continuar = Button(root, text = "Continuar", 
                                        font= "Helvetica 14 bold",
                                        command = lambda: self.client_on(self.my_username, self.optmenu))
                                        #command = lambda: self.client_on(self.entNombre.get(), self.entMenu()))
        continuar.place(relheight= 0.15, relx=0.60, rely=0.8)

    def registro(self, my_username):
        self.my_username = my_username
        #print(my_username)
        return my_username

    def guardaroption(self, optmenu):
        self.optmenu = optmenu
        #print(optmenu)
        return int(optmenu)

    def men(self, mensaj):
        self.mensaj = mensaj
        return mensaj   

    def chat_frame(self):
        #ventana del chat
        chat = Toplevel()
        chat.title('CHAT')
        chat.resizable(width=False,height=False)
        chat.configure(width = 470, height=550, bg="#17202A")
        #Lables
        lableArriba = Label(chat, bg ="#17202A", fg="#EAECEE", text ="Tu Chat", font="Helvetica 12 bold", pady=5)
        lableArriba.place(relwidth =1)
        line = Label(chat, width=450, bg ="#ABB2B9")
        line.place(relwidth=1, rely=0.07, relx=0.012)
        #area de mensajes chat
        self.textConstante = Text(chat, width = 20, height = 2, bg = "#17202A", fg = "#EAECEE", font = "Helvetica 14",  padx = 5, pady = 5)
        self.textConstante.place(relheight=0.745,relwidth=1,rely=0.08)
        lableAbajo= Label(chat, bg="#ABB2B9", height=80)
        lableAbajo.place(relwidth=1,rely=0.825)
        #entrada mensaje
        self.mensaj = StringVar()
        self.entMsg = Entry(lableAbajo, textvariable=self.mensaj, bg="#2C3E50", fg="#EAECEE", font="Helvetica 12")
        self.entMsg.place(relwidth = 0.74, relheight = 0.06, rely = 0.008, relx = 0.011) 
        self.entMsg.focus()
        #botton para mandar mensaje
        self.buttonMsg = Button(lableAbajo, 
                                text = "Enviar", 
                                font = "Helvetica 10 bold",  
                                width = 20, 
                                bg = "#ABB2B9",
                                fg="#EAECEE", 
                                command = lambda : self.writing_to_chat(self.my_username, self.entMsg.get()))
        self.buttonMsg.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
        self.textConstante.config(cursor="arrow")
        #barra para scrollear
        scrollbar= Scrollbar(self.textConstante)
        scrollbar.place(relheight = 1, relx = 0.974) 
        scrollbar.config(command = self.textConstante.yview)     
        self.textConstante.config(state = DISABLED)
    
    def juego_frame(self):
        juego = Toplevel()
        juego.title('Old Maid')
        juego.resizable(width=False,height=False)
        juego.configure(width = 600, height=500, bg="#17202A")



    def setFlagRoom(self, flag):
        flag_room = flag

    def signin(self, my_username):
        dprotocol = {
            'type': 'signin',
            'username': my_username
        }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        return msg


    def receive_message(self, client_socket,header = ''):
        """ esta función recibe los mensajes del servidor"""
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
            return msg
        except:
            return False

    def room_check(self, client_socket,header = ''):
        """ esta función recibe los mensajes del servidor"""
        try:
            if header == '': 
                message_header = client_socket.recv(HEADER_LENGTH)
            else:
                message_header = header
            if not len(message_header):
                return False
        
            message_length  = int(message_header.decode('utf-8').strip())
            data = pickle.loads(client_socket.recv(message_length))
            mes = {"header": message_header, "data": data}
            print("la verdad: ", mes['data']['type'])
            if mes['data']['type'] == 'created':
                print("\n¡nuevo room creado!\n")
            elif mes['data']['type'] == 'joined':
                print("has sido añadido al grupo numero: ", mes['data']['roomID'])
                for pl in mes['data']['players']:
                    if pl['username'] != my_username:
                        print("jugador en el mismo room que tu: ", pl['username'])
            elif mes['data']['type'] == 'already':
                print("\n¡usuario ya esta en el grupo!\n")
            return True
        except:
            return False

    def signinok(self, username,roomID):
        """ esta función avisa al servidor que el sing in fue un exito"""
        dprotocol = {
            "type":"signinok",
            "username":username,
            "roomID":roomID,
            "winner": 0,
            "is_turn": 0
        }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        return msg

    def room_id(self, client_socket, roomID, my_username):
        """ esta función avisa al servidor que numero de lobby indica un usuario"""
        dprotocol = {
            "type": "roomid",
            "username": my_username,
            "roomid": roomID
        }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        client_socket.send(msg)

    def sendmessage(self, msgtype, message, username):
        dprotocol = {
            "type":msgtype,
            "message": message,
            "username": username
        }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        client_socket.send(msg)

    def updateMessage(self, hand,username,hasQueen,numTurn):
        """ Esta funcion le manda al servidor el username del cliente,
            la mano del cliente, si tiene la old maid y el numero de turno"""
        dprotocol = {
            "type":'updateMessage',
            "hand": hand,
            "username": username,
            'hasQueen': hasQueen,
            'numTurn': numTurn
    }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        client_socket.send(msg)

    def sendPair(self, pair,hand):
        """ esta función le manda la pareja y la mano al server"""
        dprotocol = {
            "type":"sendpair",
            'pair': pair,
            'hand': hand
        }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        client_socket.send(msg)

    def pickCard(self, cardpos):
        """ Esta funcion le manda la carta que escoge de la mano del contrincante"""
        dprotocol = {
            "type":"pickCard",
            'cardpos': cardpos
        }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        client_socket.send(msg)

    def error(self, error):
        """ Esta funcion le manda un error al server"""
        dprotocol = {
            'type':"error",
            'error': error
        }
        # serializing dprotocol
        msg = pickle.dumps(dprotocol)
        # adding header to msg
        msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
        client_socket.send(msg)


    def writing_to_chat(self, my_username, mensaj):
        """ Funcion para mandar un mensaje a todos en el room <-? """
        self.mensaj = mensaj
        message = self.men(mensaj)
        try:
            #self.mensaj = mensaj
            #message = self.men(mensaj)
            #message = input("¿cúal es el mensaje? ")
            self.sendmessage("broadcast", message, my_username)
            return True
        except:
            return False

    def rooms_info(self, cs, my_username):
        """ Funcion para manejar o crear rooms """
        try:
            print("\n--------------------------------------------------------")
            print("A continuación ingrese el número identificador de su room")
            print("Si ingresa un numero que no este en sistema, se creara uno nuevo por usted")
            print("Si desea ingresar a cualquier room, manda 0")
            print("--------------------------------------------------------\n")

            while(True):
                message = input(f"{my_username} > " )
                try:
                    int(message)
                    room_id(cs, int(message), my_username)
                    return True
                except:
                    print("solo numeros")
        except:
            return False

    def thread_function(self, my_username):
        global flag_room
        global not_enough_players
        while True:
            message = self.receive_message(client_socket)
            if message:
                print(message)
                if message['data']['type'] == "message":
                    print(f"NUEVO MENSAJE de {message['data']['username']}", message['data']['message'])
                
                elif (message['data']['type'] == 'already') | (message['data']['type'] == 'created') | (message['data']['type'] == 'joined'):
                    if message['data']['type'] == 'created':
                        print("\n¡nuevo room creado!\n")
                    elif message['data']['type'] == 'joined':
                        print("\nhas sido añadido al grupo numero: ", message['data']['roomID'])
                        for pl in message['data']['players']:
                            if pl['username'] != my_username:
                                print("jugador en el mismo room que tu: \n", pl['username'])
                    elif message['data']['type'] == 'already':
                        print("\n¡usuario ya esta en el grupo!\n")

                    with lock:
                        flag_room = True
                elif (message['data']['type'] == 'you_can_play_now'):
                    print(message)
                    with game_lock:
                        not_enough_players = False

                
            if breakmech:
                break

    def client_on(self, my_username, optmenu):
        """ logica del cliente """
        global breakmech
        global client_socket
        #self.client_socket = client_socket
        #self.entMenu.delete(0,END)
        #self.optmenu = optmenu
        #int(optmenu)
        #self.entNombre.delete(0,END)
        #self.my_username = my_username
        client_off = False
        signedin = False
        #my_username = self.registro(my_username)
        #mandando mensaje de inicio al server
        self.optmenu = optmenu
        op = self.guardaroption(optmenu)
        self.my_username = my_username
        msg = self.signin(my_username)
        client_socket.send(msg)
        #print(my_username)
        #print(optmenu)
        while not client_off:
            try:
               #esperamos hasta que se complete condicion
                while not signedin:
                    #wait for useraccepted
                    message = self.receive_message(client_socket)
                    if message:
                        if message['data']['username'] == my_username:
                            # send signinok
                            print(f"Singned in server @{IP}:{PORT} as {my_username}")
                            msg = self.signinok(message['data']['username'], message['data']['roomID'])
                            client_socket.send(msg)
                            signedin = True
                        else:
                            print(f"Server thought you were {message['data']['username']}")
                            print("Disconnecting...")
                            sys.exit()
            
                flag = True
                #Iniciamos thread encargado del chat
                x = threading.Thread(target=self.thread_function, args=[my_username])
                x.start()
                while flag:
                    try:
                        if(op > 10):
                            print("Ingresa un numero del menu")
                            
                        else:
                            flag = False
                    except:
                        print("ingrese una opcion valida")     
                #determinamos que hacer en base a opcion del usuario
                if op == 1:
                    self.chat_frame()
                    #mandar mensaje a todos los de un mismo grupo
                    if not self.writing_to_chat(my_username, mensaj):
                        print("Trouble in writting room")
                elif op == 2:
                    self.juego_frame()
                   #Manejar creacion o asignacion de rooms
                    if not self.rooms_info(client_socket, my_username):
                        print("Trouble in room management")

                    while not flag_room:
                        # rc = receive_message(client_socket)
                        continue
                        # print(f'rc: {rc}')
                        # if rc:
                        #     flag_room = True
                    print(" \n----- ¡ PRONTO ESTAREAMOS JUGANDO ! -----")
                    print(" ----- esperando a los demás jugadores -----\n")
                    while not_enough_players:
                        print(" ¡espera! pronto se conectaran tus amigos")
                        time.sleep(5)
                    print("EMPIEZA OLD MAID PUES PAPA")
                        #game_function()

                elif op == 9:
                    #salir del programa
                    breakmech = True
                    print("hasta pronto")
                    x.join()
                    client_off = True

            except IOError as e:
                # errores de lectura
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print('Reading error',str(e))                        
                    exit()
                continue

            except Exception as e:
                print('General error', str(e))
                exit()

            except KeyboardInterrupt:
                print("hasta pronto")
                breakmech = True
                exit() 
root = Tk()
app = GUI()
app.main_frame(root)
root.mainloop()

