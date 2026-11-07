"""A graphics-independent 10 by 20 Tetris board."""

from __future__ import annotations

from .config import BOARD_HEIGHT, BOARD_WIDTH
from .tetromino import Piece, piece_cells


class Board:
    def __init__(self) -> None:
        self.grid: list[list[str | None]] = [
            [None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)
        ]

    def clear(self) -> None:
        for row in self.grid:
            row[:] = [None] * BOARD_WIDTH

    def can_place(self, piece: Piece) -> bool:
        for x, y in piece_cells(piece):
            if x < 0 or x >= BOARD_WIDTH or y >= BOARD_HEIGHT:
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(self, piece: Piece) -> bool:
        """Lock a valid piece. Return True if any cells were above the visible top."""
        if not self.can_place(piece):
            raise ValueError("Cannot lock a piece in a colliding position")
        topped_out = False
        for x, y in piece_cells(piece):
            if y < 0:
                topped_out = True
            else:
                self.grid[y][x] = piece.kind
        return topped_out

    def full_rows(self) -> tuple[int, ...]:
        return tuple(y for y, row in enumerate(self.grid) if all(cell is not None for cell in row))

    def clear_rows(self, rows: tuple[int, ...] | None = None) -> int:
        selected = self.full_rows() if rows is None else rows
        if not selected:
            return 0
        removed = set(selected)
        remaining = [row[:] for y, row in enumerate(self.grid) if y not in removed]
        self.grid = [[None] * BOARD_WIDTH for _ in range(len(removed))] + remaining
        return len(removed)

    def is_occupied(self, x: int, y: int) -> bool:
        return 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT and self.grid[y][x] is not None
