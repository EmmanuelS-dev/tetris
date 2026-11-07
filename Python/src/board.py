from __future__ import annotations
from .config import WIDTH, HEIGHT
from .tetromino import Piece, piece_cells

class Board:
    def __init__(self): self.grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
    def can_place(self,piece: Piece)->bool:
        for x,y in piece_cells(piece):
            if x<0 or x>=WIDTH or y>=HEIGHT: return False
            if y>=0 and self.grid[y][x] is not None: return False
        return True
    def lock_piece(self,piece: Piece)->bool:
        if not self.can_place(piece): raise ValueError("Piece collides with board")
        topout=False
        for x,y in piece_cells(piece):
            if y<0: topout=True
            else: self.grid[y][x]=piece.kind
        return topout
    def full_rows(self)->tuple[int,...]: return tuple(y for y,row in enumerate(self.grid) if all(row))
    def clear_rows(self,rows:tuple[int,...]|None=None)->int:
        selected=self.full_rows() if rows is None else rows
        if not selected:return 0
        drop=set(selected);remain=[r[:] for y,r in enumerate(self.grid) if y not in drop]
        self.grid=[[None]*WIDTH for _ in drop]+remain
        return len(drop)
