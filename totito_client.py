import socketio
import argparse
from minimax import *
from totitoChino import *

## Argument list
par=argparse.ArgumentParser(description='This is an AI that plays dots and boxes using the Minimax algorithm using alpha-beta puring an k-look ahead.')
par.add_argument('--ip','-i',dest='ip',type=str,help='IP adress of the tournament host.',required=True)
par.add_argument('--port','-p',dest='port',type=str,help='Listening port of the tournament host',required=True)
par.add_argument('--tournament','-t',dest='tournament',type=int,help='Tournament ID',required=True)
par.add_argument('--user','-u',dest='user',type=str,help='Username for this AI',required=True)


args=par.parse_args()
HOST = "http://"+args.ip+":"+args.port
USERNAME = args.user
tournamentID = args.tournament
print('Connecting to: '+HOST)
print('With username: '+USERNAME)
print('To the tournament: ', tournamentID)

sio = socketio.Client()

sio.connect(HOST)

# On connect -> signin
@sio.on('connect')
def on_connect():
    sio.emit('signin', {
        'user_name': USERNAME,
        'tournament_id': tournamentID,
        'user_role': "player"
        })
    print("Conectado: "+ USERNAME)

# On ready -> calculate move -> play
@sio.on('ready')
def on_ready(data):
    if data["player_turn_id"] == 1:
        player1 = True 
        is_max = True
    else:
        player1 = False
        is_max = False
    totito = TotitoChino(data['board'])
    movement = minimax_ab(totito,is_max=is_max,player=player1)[0]
    # movement = totito.dumb_move
    sio.emit('play',{
        'player_turn_id': data["player_turn_id"],
        'tournament_id': tournamentID,
        'game_id': data["game_id"],
        'movement': movement
    })

@sio.on('finish')
def on_finish(data):
    print('Game ',data["game_id"],' has finished')
    if data['winner_turn_id'] == data['player_turn_id']:
        print('YOU WIN!')
    else:
        print('YOU LOSE')
    print('Player id:',data['player_turn_id'])
    print('Ready to play again')
    sio.emit('player_ready', {
        'tournament_id': tournamentID,
        'game_id': data["game_id"],
        'player_turn_id': data["player_turn_id"]
    })                                                              