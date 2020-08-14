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
                self.turn = 0
                # A que jugador le toca, solo puede ser 0, 1, 2
                self.playerTurn = 0
                # Aca estaran todas las parejas que bajen los jugadores
                # las parejas las bajaremos en forma de tupla
                self.board = []
                shuffle()

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

        def isOver(self):

                
