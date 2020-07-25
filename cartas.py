class Carta:
    def __init__(self, rank, palo):
        self.rank = rank
        self.palo = palo

    def __repr__(self):
        letras = {1:'A', 11:'J', 12:'Q', 13:'K'}
        letra = letras.get(self.rank, str(self.rank))
        return "<Carta %s %s>" % (letra, self.palo)

mano = [Carta(1, 'espada'), Carta(10, 'trebol')]
