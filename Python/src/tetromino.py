from __future__ import annotations
from dataclasses import dataclass

PIECE_TYPES = ("I", "O", "T", "S", "Z", "J", "L")
SHAPES = {
 "I": ((0,0,0,0),(1,1,1,1),(0,0,0,0),(0,0,0,0)),
 "O": ((0,1,1,0),(0,1,1,0),(0,0,0,0),(0,0,0,0)),
 "T": ((0,1,0,0),(1,1,1,0),(0,0,0,0),(0,0,0,0)),
 "S": ((0,1,1,0),(1,1,0,0),(0,0,0,0),(0,0,0,0)),
 "Z": ((1,1,0,0),(0,1,1,0),(0,0,0,0),(0,0,0,0)),
 "J": ((1,0,0,0),(1,1,1,0),(0,0,0,0),(0,0,0,0)),
 "L": ((0,0,1,0),(1,1,1,0),(0,0,0,0),(0,0,0,0)),
}

@dataclass
class Piece:
    kind: str
    x: int = 3
    y: int = -1
    rotation: int = 0
    def copy(self) -> "Piece": return Piece(self.kind,self.x,self.y,self.rotation)

def local_cells(kind: str, rotation: int = 0) -> tuple[tuple[int,int],...]:
    if kind not in SHAPES: raise ValueError(f"Unknown piece {kind!r}")
    cells = [(x,y) for y,row in enumerate(SHAPES[kind]) for x,v in enumerate(row) if v]
    for _ in range(rotation % 4): cells = [(y,3-x) for x,y in cells]
    return tuple(cells)

def piece_cells(piece: Piece) -> tuple[tuple[int,int],...]:
    return tuple((piece.x+x,piece.y+y) for x,y in local_cells(piece.kind,piece.rotation))
