class Carta:
    def __init__(self, rank, palo):
        self.rank = rank
        self.palo = palo

    def __repr__(self):
        letras = {1:'A', 11:'J', 12:'Q', 13:'K'}
        letra = letras.get(self.rank, str(self.rank))
        return "<Carta %s %s>" % (letra, self.palo)

mano = [Carta(1, 'espada'), Carta(10, 'trebol')]

#o bien
import random
import itertools
SUITS = 'cdhs'
RANKS = '23456789TJQKA'
DECK = tuple(''.join(card) for card in itertools.product(RANKS, SUITS))
hand = random.sample(DECK, 5)
print hand
['Kh', 'Kc', '6c', '7d', '3d']