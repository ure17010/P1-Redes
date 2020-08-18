# Juego de cartas:
## Old Maid
### Explicación e historia:
Old Maid es el nombre de un juego de cartas simple que requiere al menos dos jugadores pero puede llegar hasta 8 jugadores.
La traducción lógica para Old Maid es <Solterona>. 
En esencia una solterona es una mujer que no está casada. Es una frase despectiva que se utiliza para describir a una mujer que se considera "vieja" y que no tiene marido.
La frase <solterona> ha existido al menos desde la época victoriana (aunque podria ser desde antes). En aquel entonces, la idea de que una mujer permaneciera soltera era impactante. 
El juego ha existido desde dicha época. 
En resumen, el juego requiere que los jugadores intenten evitar quedarse atrapados con la tarjeta Old Maid.
Mientras bajan parejas por turnos para que acabe el juego solo con dicha tarjeta.
El juego reforzó las reglas sociales de la época. Implica que las mujeres deben casarse cuando sean jóvenes para no terminar siendo una solterona. 
También implicaba que los hombres debían casarse con una mujer joven para evitar quedarse atrapados con una solterona.
Old Maid se juega con una baraja estándar de 52 cartas. Se consideraba que la reina negra era la vieja solterona. 
Una de las otras tres reinas se eliminó del mazo para asegurarse de que la carta de Old Maid no coincidiera.

### Protocolo

    dprotocol = {
        'type': 'cardPick',
        'oldmaid': oldmaid
    }

    dprotocol = {
        'type': 'room',
        'type2': type_msg,
        'roomID': roomid,
        'players': players
    }

    dprotocol = {
        'type': 'useraccepted',
        'username': username,
        'roomID': 1
    }

    room = {
        "players": [client],
        "time_connection": [time]
    }

    dprotocol = {
        'type': 'message',
        'username': username,
        'message': message
    }

    dprotocol = {
            'type': 'you_can_play_now',
            'players': OldMaid.getPlayers(),
            'oldmaid': OldMaid
        }

    dprotocol = {
        'type': 'all_pairs_down',
        'oldmaid': oldmaid
    }

    dprotocol = {
        'type': 'pairsOk',
        'oldmaid': oldmaid
    }

    dprotocol = {
        'type': 'signin',
        'username': my_username
    }

    dprotocol = {
        "type":"signinok",
        "username":username,
        "roomID":roomID,
        "winner": 0,
        "turn": 0,
        "hand": []
    }

    dprotocol = {
        "type": "roomid",
        "username": my_username,
        "roomid": roomID
    }

    dprotocol = {
        "type":msgtype,
        "message": message,
        "username": username
    }

    dprotocol = {
        "type":'updateMessage',
        "hand": hand,
        "username": username,
        'hasQueen': hasQueen,
        'numTurn': numTurn
    }

    dprotocol = {
        "type":"sendpair",
        'pair': pair,
        'hand': hand
    }

    dprotocol = {
        "type":'im_done',
        "room_id": roomid,
        "username": username,
        "hand": hand
    }

    dprotocol = {
        "type":"pickCard",
        'cardpos': cardpos,
        'room_id': roomid
    }

    dprotocol = {
        'type':"error",
        'error': error
    }

### Instalaciones:
No se requiere la instalación de ninguna librería ya que las utilizadas vienen en el estándar. 
### Librerias utilizadas:
import socket
import select
import errno
import sys
import pickle
import threading
import time
import itertools
import random
import datetime

### Versiones y para la ejecución:
#### Local:
Para la ejecución local del programa es importante primero descargarlo en github y clonar. 
En la ubicación de la carpeta correr en la terminal el archivo server.py para inicializarlo. 
#### Online:
Ip: 18.222.142.27
Se ha implementado el uso de Amazon Web Services (aws). 
Esto para montar el servidor en la nube y se incluyen todos los datos de conexión.

#### Para correr el servidor en local

    python server-test.py

#### Para correr el cliente en local 

    python client-test.py

#### Para correr el cliente con el servidor en amazon ec2 

    python client-cloud.py