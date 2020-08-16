"""
Universidad del Valle de Guatemala 
Redes
CAtedrático: Vinicio Paz

Estuardo Ureta - Oliver Mazariegos - Pablo Viana

-> Logica del juego Old Maid
"""

import itertools, random

class OldMaid(object):
        def __init__(self,players):
                # Lista de jugadores. Cada jugador es un diccionario
                self.players = players
                # Turnos globales
                self.turn = 1
                # A que jugador le toca, solo puede ser 0, 1, 2
                self.playerTurn = 0
                # Aca estaran todas las parejas que bajen los jugadores
                # las parejas las bajaremos en forma de tupla
                self.board = []
                self.shuffle()

        # Funcion que genera un deck, lo revuelve y reparte cartas a cada jugador
        def shuffle(self):
                # crea deck
                deck = list(itertools.product(range(1,14),['Spade','Heart','Diamond','Club']))
                # revuelve deck
                random.shuffle(deck)
                # quita las Qs: 12
                deck.remove((12,'Heart'))
                deck.remove((12,'Club'))
                deck.remove((12,'Diamond'))
                player = 0
                # Repartición de cartas
                for card in deck:
                        # Da carta a un jugador
                        self.players[player]['hand'].append(card)
                        if player == 2: player = 0
                        else: player += 1

        def nextTurn(self):
                if self.playerTurn == 2:
                        self.playerTurn = 0
                else: self.playerTurn += 1
                self.turn += 1

        # Funcion que detecta quienes son los ganadores
        def winners(self):
                ganadores = []
                for player in self.players:
                        if not player['hand']: ganadores.append(player['username'])
                return ganadores

        # Fucnion que checkea si ya termino el juego, si si devuelve los ganadores
        def isOver(self):
                if len(self.board) == 24: return self.winners()
                else: False

        # Función que chequea si jugador tiene parejas y la devuelve
        def hasPair(self, playerIndex):
                hand = self.players[playerIndex]['hand']
                for i in range(len(hand)):
                        current = hand[i]
                        for j in range(len(hand)):
                                possible = hand[j]
                                # Chequea si hay pareja
                                if current[0] == possible[0]:
                                        # Se le quita la pareja al jugador
                                        pareja = (self.players[playerIndex]['hand'].pop(j), self.players[player]['hand'].pop(i))
                                        # Se agrega la pareja al board
                                        self.board.append(pareja)
                                        return pareja
                return False

        # Función que lista los posibles movimientos
        def listMoves(self):
                if self.playerTurn == 0:
                        oponent = 2
                else:
                        oponent = self.playerTurn - 1
                return list(range(len(self.players[oponent]['hand'])))

        # Función que hace un movimiento. Recibe el index de la carta que quiere robar el jugador 
        def move(self, cardPicked):
                if self.playerTurn == 0:
                        oponent = 2
                else:
                        oponent = self.playerTurn - 1
                # Se le quita carta al jugador a la derecha, y se le agrega a la mano del jugador actual
                self.players[self.playerTurn]['hand'].append(self.player[oponent]['hand'].pop(cardPicked))
                # Se detecta si hay una pareja
                pareja = self.hasPair(self.playerTurn)
                # Se actualiza el turno del jugador
                self.nextTurn()
                # Se devuelve la pareja que se encontró
                return pareja

        def getStatus(self):
                return {
                        'turn': self.turn,
                        'board': self.board,
                        'players': self.players
                        'index_of_player_in_turn': self.playerTurn
                }
