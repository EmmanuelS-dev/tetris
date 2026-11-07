import random
from .tetromino import PIECE_TYPES

class PieceGenerator:
    def __init__(self,seed=None): self.random=random.Random(seed);self.bag=[]
    def next_piece(self):
        if not self.bag:
            self.bag=list(PIECE_TYPES);self.random.shuffle(self.bag)
        return self.bag.pop()
