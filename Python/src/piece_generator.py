"""Seven-bag tetromino generator."""

from __future__ import annotations

import random

from .tetromino import PIECE_TYPES, PieceType


class PieceGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)
        self._bag: list[PieceType] = []

    def next_piece(self) -> PieceType:
        if not self._bag:
            self._bag = list(PIECE_TYPES)
            self._random.shuffle(self._bag)
        return self._bag.pop()
