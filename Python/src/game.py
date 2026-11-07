"""Core Tetris rules; this module has no Pygame dependency."""

from __future__ import annotations

from enum import Enum

from .board import Board
from .config import NEXT_QUEUE_SIZE
from .piece_generator import PieceGenerator
from .tetromino import PIECE_TYPES, Piece, PieceType

LINE_POINTS = (0, 100, 300, 500, 800)


class Screen(str, Enum):
    MENU = "menu"
    CONTROLS = "controls"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"


# Coordinates use screen space (positive y points downward).
_JLSTZ_KICKS = (
    ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
    ((0, 0), (1, 0), (1, 1), (0, -2), (1, -2)),
    ((0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)),
    ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
    ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)),
    ((0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)),
    ((0, 0), (1, 0), (1, -1), (0, 2), (1, 2)),
)
_I_KICKS = (
    ((0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)),
    ((0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)),
    ((0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)),
    ((0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)),
    ((0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)),
    ((0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)),
    ((0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)),
    ((0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)),
)


class Game:
    def __init__(self, seed: int | None = None, high_score: int = 0) -> None:
        self.high_score = max(0, high_score)
        self.state = Screen.MENU
        self.events: list[tuple[str, object | None]] = []
        self.start_game(seed)
        self.state = Screen.MENU

    def start_game(self, seed: int | None = None) -> None:
        best = getattr(self, "high_score", 0)
        self.board = Board()
        self.generator = PieceGenerator(seed)
        self.next_queue = [self.generator.next_piece() for _ in range(NEXT_QUEUE_SIZE)]
        self.held: PieceType | None = None
        self.hold_used = False
        self.score = 0
        self.lines = 0
        self.level = 1
        self.gravity_timer = 0.0
        self.active = self._take_next()
        self.state = Screen.PLAYING
        self.high_score = best
        self.events = []
        if not self.board.can_place(self.active):
            self._game_over()

    def _take_next(self) -> Piece:
        kind = self.next_queue.pop(0)
        self.next_queue.append(self.generator.next_piece())
        self.hold_used = False
        return Piece(kind)

    def add_score(self, points: int) -> None:
        if points <= 0:
            return
        self.score += points
        self.high_score = max(self.high_score, self.score)
        self.events.append(("score", points))

    @property
    def gravity_interval(self) -> float:
        return max(0.05, 0.8 - (self.level - 1) * 0.065)

    def move(self, dx: int, dy: int) -> bool:
        if self.state != Screen.PLAYING:
            return False
        candidate = self.active.copy()
        candidate.x += dx
        candidate.y += dy
        if not self.board.can_place(candidate):
            return False
        self.active = candidate
        if dx:
            self.events.append(("move", None))
        return True

    def soft_drop(self) -> bool:
        if not self.move(0, 1):
            return False
        self.add_score(1)
        self.events.append(("soft_drop", None))
        return True

    def rotate(self, direction: int = 1) -> bool:
        if self.state != Screen.PLAYING or direction == 0:
            return False
        if self.active.kind == "O":
            return True
        old_rotation = self.active.rotation % 4
        new_rotation = (old_rotation + (1 if direction > 0 else -1)) % 4
        transition = old_rotation * 2 + (0 if direction > 0 else 1)
        kicks = _I_KICKS[transition] if self.active.kind == "I" else _JLSTZ_KICKS[transition]
        for dx, dy in kicks:
            candidate = Piece(
                self.active.kind,
                self.active.x + dx,
                self.active.y + dy,
                new_rotation,
            )
            if self.board.can_place(candidate):
                self.active = candidate
                self.events.append(("rotate", None))
                return True
        return False

    def ghost_piece(self) -> Piece:
        ghost = self.active.copy()
        while self.board.can_place(Piece(ghost.kind, ghost.x, ghost.y + 1, ghost.rotation)):
            ghost.y += 1
        return ghost

    def hard_drop(self) -> int:
        if self.state != Screen.PLAYING:
            return 0
        distance = 0
        while self.move(0, 1):
            distance += 1
        self.add_score(distance * 2)
        self.events.append(("hard_drop", None))
        self.lock_piece()
        return distance

    def hold_piece(self) -> bool:
        if self.state != Screen.PLAYING or self.hold_used:
            return False
        current = self.active.kind
        if self.held is None:
            self.held = current
            self.active = self._take_next()
        else:
            swap = self.held
            self.held = current
            self.active = Piece(swap)
            if not self.board.can_place(self.active):
                self._game_over()
                return False
        self.hold_used = True
        self.gravity_timer = 0.0
        self.events.append(("hold", None))
        return True

    def lock_piece(self) -> int:
        if self.state != Screen.PLAYING:
            return 0
        topped_out = self.board.lock_piece(self.active)
        self.events.append(("lock", None))
        if topped_out:
            self._game_over()
            return 0
        full_rows = self.board.full_rows()
        cleared = self.board.clear_rows(full_rows)
        if cleared:
            score = LINE_POINTS[min(cleared, 4)] * self.level
            self.add_score(score)
            self.lines += cleared
            self.events.append(("clear", full_rows))
            if cleared == 4:
                self.events.append(("tetris", None))
            old_level = self.level
            self.level = 1 + self.lines // 10
            if self.level > old_level:
                self.events.append(("level", self.level))
        self.active = self._take_next()
        self.gravity_timer = 0.0
        if not self.board.can_place(self.active):
            self._game_over()
        return cleared

    def update(self, dt: float) -> None:
        if self.state != Screen.PLAYING or dt <= 0.0:
            return
        self.gravity_timer += min(dt, 0.25)
        interval = self.gravity_interval
        while self.gravity_timer >= interval and self.state == Screen.PLAYING:
            self.gravity_timer -= interval
            if not self.move(0, 1):
                self.lock_piece()
                break

    def toggle_pause(self) -> None:
        if self.state == Screen.PLAYING:
            self.state = Screen.PAUSED
        elif self.state == Screen.PAUSED:
            self.state = Screen.PLAYING

    def _game_over(self) -> None:
        self.state = Screen.GAME_OVER
        self.events.append(("game_over", None))
