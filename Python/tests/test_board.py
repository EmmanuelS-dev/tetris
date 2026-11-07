import pytest
from src.board import Board
from src.tetromino import Piece

def test_boundaries_collision_and_hidden_spawn():
    b=Board();assert b.can_place(Piece("T",3,-1));assert not b.can_place(Piece("O",-2,5));assert not b.can_place(Piece("O",9,5));assert not b.can_place(Piece("O",3,19))
    b.grid[7][5]="I";assert not b.can_place(Piece("O",4,6))
def test_lock_identity_and_topout():
    b=Board();assert not b.lock_piece(Piece("J",3,18));assert b.grid[18][3]=="J" and b.grid[19][4]=="J"
    assert b.lock_piece(Piece("T",3,-2))
    with pytest.raises(ValueError):b.lock_piece(Piece("O",-2,0))
def test_single_and_multiple_row_clear_shift_down():
    for count in range(1,5):
        b=Board()
        for y in range(20-count,20):b.grid[y]=["J"]*10
        b.grid[0][0]="T";assert b.clear_rows()==count;assert b.grid[count][0]=="T";assert all(not any(row) for row in b.grid[:count])
