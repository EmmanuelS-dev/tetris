import pytest

from src.board import Board
from src.tetromino import Piece


def test_valid_and_invalid_movement_and_collision():
    board = Board()
    piece = Piece("O", x=3, y=5)
    assert board.can_place(piece)
    assert board.can_place(Piece("O", x=2, y=5))
    assert not board.can_place(Piece("O", x=-2, y=5))
    assert not board.can_place(Piece("O", x=9, y=5))
    assert not board.can_place(Piece("O", x=3, y=19))


def test_collision_with_locked_cell():
    board = Board()
    board.grid[7][5] = "T"
    assert not board.can_place(Piece("O", x=4, y=6))
    assert board.can_place(Piece("O", x=1, y=6))


def test_piece_locks_with_its_identity():
    board = Board()
    assert not board.lock_piece(Piece("J", x=3, y=18))
    assert board.grid[18][4:7] == ["J", "J", "J"]
    assert board.grid[19][4] == "J"


def test_lock_rejects_collision():
    board = Board()
    board.grid[19][4] = "L"
    with pytest.raises(ValueError):
        board.lock_piece(Piece("O", x=3, y=18))


def test_hidden_spawn_cells_are_allowed_but_reported_on_lock():
    board = Board()
    piece = Piece("T", x=3, y=-2)
    assert board.can_place(piece)
    assert board.lock_piece(piece)
