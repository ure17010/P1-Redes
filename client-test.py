"""
Universidad del Valle de Guatemala 
Redes
CAtedrático: Vinicio Paz
Estuardo Ureta - Oliver Mazariegos - Pablo Viana
-> Un cliente para un servidor en python para jugar old maid
"""

# importamos librerias
import socket
import select
import errno
import sys
import pickle
import threading
import time
import itertools
#Importamos clase OldMaid()
import oldmaid as om
# variables globales
HEADER_LENGTH = 10 
IP = "127.0.0.1"
PORT = 5555
breakmech = False
flag_room = False
pairs_not_down = True
not_enough_players = True
not_my_turn = True
players_in_ma_room = []
lock = threading.RLock()
#un lock para cada variable ¿? no sé 
game_lock = threading.RLock()

dummy = []
for i in range(3):
    dummyPlayer = {
        'username':'',
        'hand':[]
    }
    dummy.append(dummyPlayer)
serverOldMaid = om.OldMaid(dummy, False)


# make conncection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP,PORT))
client_socket.setblocking(False)
print(f"Connected to server in {IP}:{PORT}")

def setFlagRoom(flag):
    flag_room = flag

def signin(my_username):
    dprotocol = {
        'type': 'signin',
        'username': my_username
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg


def receive_message(client_socket,header = ''):
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

def signinok(username,roomID):
    """ esta función avisa al servidor que el sing in fue un exito"""
    dprotocol = {
        "type":"signinok",
        "username":username,
        "roomID":roomID,
        "winner": 0,
        "turn": 0,
        "hand": []
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    return msg

def room_id(client_socket, roomID, my_username):
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

def sendmessage(msgtype, message, username):
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

def updateMessage(hand,username,hasQueen,numTurn):
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

def sendPair(pair,hand):
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

def im_done(roomid,hand,username):
    dprotocol = {
        "type":'im_done',
        "room_id": roomid,
        "username": username,
        "hand": hand
    }
    # serializing dprotocol
    msg = pickle.dumps(dprotocol)
    # adding header to msg
    msg = bytes(f"{len(msg):<{HEADER_LENGTH}}", "utf-8") + msg
    client_socket.send(msg)


def pickCard(cardpos):
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

def error(error):
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


def menu():
    """ Funcion que se encarga del menu del cliente """

    #os.system('clear')  NOTA para windows tienes que cambiar clear por cls
    print ("Selecciona una opción")
    print ("\t1 - mandar mensaje")
    print ("\t2 - jugar")
    print ("\t9 - salir")

def writing_to_chat(my_username):
    """ Funcion para mandar un mensaje a todos en el room <-? """
    try:
        message = input("¿cúal es el mensaje? ")
        sendmessage("broadcast", message, my_username)
        return True
    except:
        return False

def rooms_info(cs, my_username):
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

def thread_function(my_username):
    global flag_room
    global not_enough_players
    global pairs_not_down
    global not_my_turn
    global players_in_ma_room
    global serverOldMaid
    while True:
        message = receive_message(client_socket)
        if message:
            if message['data']['type'] == "message":
                print(f"NUEVO MENSAJE de {message['data']['username']}", message['data']['message'])
            elif (message['data']['type'] == 'room'):
                if message['data']['type2'] == 'created':
                    print("\n¡nuevo room creado!\n")
                elif message['data']['type2'] == 'joined':
                    print("\nhas sido añadido al grupo numero: ", message['data']['roomID'])
                    for pl in message['data']['players']:
                        if pl['username'] != my_username:
                            print("jugador en el mismo room que tu: \n", pl['username'])
                elif message['data']['type2'] == 'already':
                    print("\n¡usuario ya esta en el grupo!\n")
                with lock:
                    flag_room = True
            elif (message['data']['type'] == 'you_can_play_now'):
                with game_lock:
                    players_in_ma_room = message['data']['players']
                    not_enough_players = False
            elif (message['data']['type'] == 'all_pairs_down'):
                serverOldMaid = message['data']['oldmaid']
                pairs_not_down = False
            elif (message['data']['type'] == 'your_turn'):
                not_my_turn = False
        if breakmech:
            break

def pairs_down(game_oldmaid, playerIndex, my_username,roomid):
    """Esta funcion es la encargada de la jugabilidad de bajar las parejas de cartas"""
    #no hay progra defensiva todavia
    hand = []
    while game_oldmaid.hasPair(playerIndex):
        status = game_oldmaid.getStatus()
        for pl in status['players']:
            if pl["username"] == my_username:
                print("\n------> MI MANO: ", pl['hand'])
        key = input("¿qué pareja bajas a la mesa? ")
        response = game_oldmaid.isPair(playerIndex, int(key))
        if response == True:
            print("\nPareja bajada!\n")
        else:
            print("\nNo existe una pareja con ese numero\n")
    
    status = game_oldmaid.getStatus()
    for pl in status['players']:
        if pl['username'] == my_username:
            hand = pl['hand']


                        
    print("\n    _____  ")
    print("  _|  __ \ ")
    print(" (_) |  | |")
    print("   | |  | | ¡Parece que ya no hay más parejas!")
    print("   | |  | |")
    print("  _| |__| |")
    print(" (_)_____/ \n")


    im_done(roomid,hand,my_username)

    return True


def client_on():
    """ logica del cliente """
    global breakmech
    global client_socket
    global pairs_not_down
    global not_my_turn
    client_off = False
    signedin = False
    game_on = True
    
    #mandando mensaje de inicio al server
    my_username = input("Username: ")
    msg = signin(my_username)
    client_socket.send(msg)
    while not client_off:
        try:
            #esperamos hasta que se complete condicion
            while not signedin:
                #wait for useraccepted
                message = receive_message(client_socket)
                if message:
                    if message['data']['username'] == my_username:
                        # send signinok
                        print(f"Singned in server @{IP}:{PORT} as {my_username}")
                        msg = signinok(message['data']['username'], message['data']['roomID'])
                        client_socket.send(msg)
                        signedin = True
                    else:
                        print(f"Server thought you were {message['data']['username']}")
                        print("Disconnecting...")
                        sys.exit()
            menu()
            flag = True
            #Iniciamos thread encargado del chat
            x = threading.Thread(target=thread_function, args=[my_username])
            x.start()
            while flag:
                # programación defensiva
                try:
                    optmenu = int(input(f"{my_username} > "))
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
                if not writing_to_chat(my_username):
                    print("Trouble in writting room")
            elif optmenu == 2:
                #Manejar creacion o asignacion de rooms
                if not rooms_info(client_socket, my_username):
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

                # ------------------------------ AQUI EMPIEZA OLD MAID ------------------------------
                copy = True
                game_oldmaid = om.OldMaid(players_in_ma_room,True)
                roomid = game_oldmaid.getPlayers()[0]['roomID']
                decition_flag = True
                print("\n\n    ______    ___       ________       ___      ___       __        __     ________   ")
                print("   /      \  |   |     |        \     |   \    /   |     /  \      |  \   |        \  ")
                print("  // ____  \ ||  |     (.  ___  :)     \   \  //   |    /    \     ||  |  (.  ___  :) ")
                print(" /  /    ) :)|:  |     |: \   ) ||     /\\  \/.    |   /' /\  \    |:  |  |: \   ) || ")
                print("(: (____/ //  \  |___  (| (___\ ||    |: \.        |  //  __'  \   |.  |  (| (___\ || ")
                print(" \        /  ( \_|:  \ |:       :)    |.  \    /:  | /   /  \\  \  /\  |\ |:       :) ")
                print("  \"_____/    \_______)(________/     |___|\__/|___|(___/    \___)(__\_|_)(________/  \n\n")
                while game_on:
                    status = game_oldmaid.getStatus()
                    #primer turno
                    if(status['turn'] == 1):
                        print("\n\nEs el primer turno, por lo que debes armar parejas con las cartas de tu mano")
                        print("Para hacerlo, solo debes escribir el número de la carta que tiene una pareja")
                        print("Por ejemplo, si yo tuviera en mi mano [...(2, 'Diamond'), (2, 'Heart')...]")
                        print("Solo debo escribir: 2 para armar la pareja\n\n")
                        cont = 0
                        for pl in status['players']:
                            if pl["username"] == my_username:
                                playerIndex = cont
                            cont += 1

                        pairs_down(game_oldmaid, playerIndex, my_username,roomid)

                        print("esperando a que todos bajen sus cartas")
                        while pairs_not_down:
                            continue
                        game_oldmaid = serverOldMaid
                        #self.updateMessage()
                        

                    status2 = game_oldmaid.getStatus()
                    if(playerIndex == status2['index_of_player_in_turn']):
                        print("\n-----! ES TU TURNO !-----")
                        status3 = game_oldmaid.getStatus()
                        print(f"debes quitar una carta de la mano de {status3['oponent']['username']}")
                        print(f"{status3['oponent']['username']} tiene {len(status3['oponent']['hand'])} cartas")
                        visualization = list(itertools.product(range(len(status3['oponent']['hand'])),['carta desconocida']))                        
                        print("\n\n", visualization)
                        decition = int(input("¿que carta deseas quitar al oponente? (? empieza en 0) "))
                        while decition_flag:
                            if decition > len(status['oponent']['hand']):
                                print("\n¡tu oponente no tiene tantas cartas!")
                                decition = int(input("¿que carta deseas quitar al oponente? (? empieza en 0) "))
                            else:
                                decition_flag = False
                        game_oldmaid.move(decition)
                        pairs_down(game_oldmaid, playerIndex, my_username, roomid)
                        not_my_turn = True
                    else:
                        print(f"!---- AHORA ES EL TURNO DE {status['player_in_turn']['username']}")

                    while not_my_turn:
                        continue

                #game_function()
                # ------------------------------ AQUI TERMINA OLD MAID ------------------------------
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

        # except Exception as e:
        #     print('General error', str(e))
        #     exit()

        except KeyboardInterrupt:
            print("hasta pronto")
            breakmech = True
            exit()


if __name__ == "__main__":
    try:
        client_on()
    except KeyboardInterrupt:
        print("hasta pronto")
        exit()
