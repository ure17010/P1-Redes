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

# variables globales
HEADER_LENGTH = 10 
IP = "127.0.0.1"
PORT = 5555
breakmech = False

# make conncection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)
print(f"Connected to server in {IP}:{PORT}")

class GUI:
    #metodo
    def __init__(self):

        #ventana del chat (no se mira aun)
        #self.Ventana = Tk()
        #self.Ventana.withdraw()

        #venatana menu
        self.root = Tk()
        self.root.withdraw()

        #Ventana de Login
        self.login = Toplevel()
        self.login.title("Ingreso Cliente")

        #Ventana menu
        #self.menu = Toplevel()
        #self.menu.title("Menú")

        #Inmovible y tamaños
        self.login.resizable(width = False, height = False)
        self.login.configure(width = 500, height = 400)

        #Labels USUARIO e Instrucciones de login
        self.pls = Label(self.login, text = "Porfavor ingresa tu usuario y el # de opción  para continuar", justify = CENTER, font = "Helvetica 10 bold") 
        self.pls.place(relheight = 0.15, relx = 0.1, rely = 0.07) 
 
        self.labelName = Label(self.login, text = "Usuario: ", font = "Helvetica 12") 
        self.labelName.place(relheight = 0.2, relx = 0.1, rely = 0.2)
        
        #caja para escribir usuario
#        input_user = StringVar()
        self.entNombre = Entry(self.login)#, text=input_user)
        self.entNombre.place(relwidth = 0.4,  relheight = 0.12, relx = 0.35, rely = 0.2)
        self.entNombre.focus()
        

        #Boton para continuar
        self.go = Button(self.login,text = "Ingresar",
                                    font="Helvetica 15 bold", 
                                    command = lambda: self.client_on(self.entNombre.get(), self.entMenu.get()))
        self.go.place(relx=0.4, rely=0.45)

        

        #labels opciones
        self.opcion1 = Label(self.login, text="1. Mandar mensaje", justify = CENTER, font = "Helvetica 8 bold")
        self.opcion1.place(relheight = 0.15, relx = 0.2, rely = 0.65)
        self.opcion2 = Label(self.login, text="2. Jugar", justify = CENTER, font = "Helvetica 8 bold")
        self.opcion2.place(relheight = 0.15, relx = 0.2, rely = 0.75)
        self.opcion9 = Label(self.login, text="9. Salir", justify = CENTER, font = "Helvetica 8 bold")
        self.opcion9.place(relheight = 0.15, relx = 0.2, rely = 0.85)

        #Entrada para elegir opción
        self.entMenu = Entry(self.login)
        self.entMenu.place(relwidth = 0.15, relheight=0.07, relx = 0.45, rely=0.757)
        self.entMenu.focus()

        self.root.mainloop()
    
    def client_on(self, my_username, optmenu):
        #recibe variable ingresada en entry y borra valor incial
        self.entNombre.delete(0,END)
        self.my_username = my_username
        #otra variable optmenu
        self.entMenu.delete(0,END)
        self.optmenu = optmenu
        #destuye ventana de login tras apachar btn
        self.login.destroy() 

        global breakmech
        singedin = False
        client_off = False
        flag_room = False
        msg = self.signin(my_username)

        client_socket.send(msg)
        while not client_off:
            try:
                #esperamos hasta que se complete la accion
                while not singedin:
                    #wait for useraccepted
                    message = self.receive_message(client_socket)
                    #print(message)
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
                # variable para contrlar el while
                flag = True
                x = threading.Thread(target=thread_function, args=[my_username])
                x.start()
                while flag:
                # programación defensiva
                    try:
                        if(optmenu > 10):
                            print("Ingresa un numero del menu")
                            menu()
                        else:
                            flag = False
                    except:
                        print("ingrese una opcion valida")
                        menu()

                #determinamos que hacer en base a opcion del usuario
                if optmenu == 1:
                    #mandar mensaje a todos los de un mismo grupo
                    if not self.writing_to_chat(my_username):
                        print("Trouble in writting room")
                elif optmenu == 2:
                    #Manejar creacion o asignacion de rooms
                    if not self.rooms_info(my_username):
                        print("Trouble in room management")
                    while not flag_room:
                        rc = room_check(client_socket)
                        if rc == True:
                            flag_room = True

                elif optmenu == 9:
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

    def receive_message(self, client_socket, header = ''):
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
            return {"header": message_header, "data": data}
        except:
            return False

    def room_id(self, roomID, my_username):
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

    def updateMessage(self,hand,username,hasQueen,numTurn):
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


    def menu(self, optmenu):
        """ Funcion que se encarga del menu del cliente """
        self.entMenu.delete(0,END)
        self.optmenu = optmenu
        #os.system('clear')  NOTA para windows tienes que cambiar clear por cls
        print ("Selecciona una opción")
        print ("\t1 - mandar mensaje")
        print ("\t2 - jugar")
        print ("\t9 - salir")

    def writing_to_chat(self, my_username):
        """ Funcion para mandar un mensaje a todos en el room <-? """
        try:
            message = input("¿cúal es el mensaje? ")
            sendmessage("broadcast", message, my_username)
            return True
        except:
            return False

    def rooms_info(self, my_username):
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
                    room_id(int(message), my_username)
                    return True
                except:
                    print("solo numeros")
        except:
            return False

    def thread_function(self, my_username):
        while True:
            message = receive_message(client_socket)
            if message:
                if message['data']['type'] == "message":
                    print(f"NUEVO MENSAJE de {message['data']['username']}", message['data']['message'])
                    menu()
                    print(f"{my_username} > ")
            if breakmech:
                break
'''
    def show_menu(self, my_username):
        self.my_username = my_username
        #enseña ventana menu
        self.root.deiconify()
        self.root.title("Menu")
        self.root.resizable(width=False,height=False)
        self.root.configure(width = 400, height=300, bg="grey")
        #labels opciones
        self.opcion1 = Label(self.root, text="1. Mandar mensaje", justify = CENTER, font = "Helvetica 10 bold")
        self.opcion1.place(relheight = 0.15, relx = 0.2, rely = 0.07)
        self.opcion2 = Label(self.root, text="2. Jugar", justify = CENTER, font = "Helvetica 10 bold")
        self.opcion2.place(relheight = 0.15, relx = 0.2, rely = 0.17)
        self.opcion9 = Label(self.root, text="9. Salir", justify = CENTER, font = "Helvetica 10 bold")
        self.opcion9.place(relheight = 0.15, relx = 0.2, rely = 0.27)
        #botton opciones
        self.btn1 = Button(self.root, text="Selccionar opcion", font="Helvetica 10 bold", command = lambda: self.menu(self.entMenu.get()) )
        self.btn1.place(relx = 0.05, rely=0.47)
        #Entrada para elegir opción
        self.entMenu = Entry(self.root)
        self.entMenu.place(relwidth = 0.15, relheight=0.07, relx = 0.45, rely=0.47)
        self.entMenu.focus()
        '''
        
g = GUI()
'''
    def layout(self, usuario):
    #enseñar ventana de chat
    self.Ventana.deiconify()
    self.Ventana.title("Chat")
    #inmovible
    self.Ventana.resizable(width=False,height=False)
    self.Ventana.configure(width = 470, height=550, bg="#17202A")
    #Labels
    self.lableArriba = Lable(self.Ventana, bg ="#17202A", fg="#EAECEE", text =self.usuario, font="Helvetica 12 bold", pady=5)
    self.lableArriba.place(relwidth =1)
    self.line = Lable(self.Ventana, width=450, bg "#ABB2B9")
    self.textConstante = Text(self.Ventana, width = 20, height = 2, bg = "#17202A", fg = "#EAECEE", font = "Helvetica 14",  padx = 5, pady = 5))
    self.textConstante.place(relheight=0.745,relwidth=1,rely=0.08)
    self.lableAbajo= Lable(self.Ventana, bg="ABB2B9",height=80)
    self.lableAbajo.place(relwidth=1,rely=0.825)
    #entrada mensajes
    self.entMsg = Entry(self.lableAbajo, bg="#2C3E50", fg="#EAECEE", font="Helvetica 12")
    self.entMsg.place(relwidth = 0.74, relheight = 0.06, rely = 0.008, relx = 0.011) 
    self.entryMsg.focus() 
    #botton de mandar mensaje
    self.buttonMsg = Button(self.labelBottom, 
                                text = "Enviar", 
                                font = "Helvetica 10 bold",  
                                width = 20, 
                                bg = "#ABB2B9", 
                                command = lambda : self.sendButton(self.entMsg.get()))
    self.buttonMsg.place(relc=0.77, rely=0.008, relheight=0.06, relwidth=0.22)
    self.textConstante.config(cursor="arrow")
    #barra para scrollear
    scrollbar= Scrollbar(self.textConstante)
    scrollbar.place(relheight = 1, relx = 0.974) 
    scrollbar.config(command = self.textConstante.yview)     
    self.textConstante.config(state = DISABLED) 

#Funciones que mueven toa la cuestion
   '''
'''
#primera ventana
ventana1 = tk.Tk()
ventana1.title("Client")

#ingreso de usuario y connexion
topFrame =tk.Frame(ventana1)
lblNombre = tk.Label(topFrame, text = "Usuario:")
lblNombre.pack(side=tk.LEFT)
entNombre = tk.Entry(topFrame)
entNombre.pack(side=tk.LEFT)
bottonSingin = tk.Button(topFrame, text = "Connectar", command = lambda: recibeUser)
bottonSingin.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP)



def recibeUser():
    while entNombre == len(0):
        x1 = entNombre.get()
        b = x1.encode('utf-8')
        client_socket.send(b)
        return b
    else:
        pass

    '''

if __name__ == "__main__":
    try:
        client_on()
    except KeyboardInterrupt:
        print("Hasta pronto")
        exit()
