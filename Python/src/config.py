"""Shared game dimensions, colors, and local data paths."""

from __future__ import annotations

import os
from pathlib import Path

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
NEXT_QUEUE_SIZE = 5
FPS = 60
WINDOW_SIZE = (1120, 800)
MIN_WINDOW_SIZE = (880, 640)

BACKGROUND_TOP = (248, 247, 243)
BACKGROUND_BOTTOM = (239, 239, 234)
SURFACE = (255, 255, 253)
BOARD_SURFACE = (250, 250, 247)
INK = (40, 47, 54)
MUTED = (121, 129, 135)
GRID = (229, 231, 226)
ACCENT = (51, 132, 119)
ACCENT_SOFT = (223, 239, 234)
SHADOW = (37, 49, 54, 25)
PIECE_COLORS = {
    "I": (91, 174, 186),
    "O": (220, 177, 91),
    "T": (151, 123, 178),
    "S": (113, 166, 132),
    "Z": (205, 113, 112),
    "J": (103, 133, 184),
    "L": (209, 145, 91),
}


def high_score_path() -> Path:
    """Return a user-writable platform data path without extra dependencies."""
    if os.name == "nt" and os.getenv("APPDATA"):
        root = Path(os.environ["APPDATA"])
    elif os.getenv("XDG_DATA_HOME"):
        root = Path(os.environ["XDG_DATA_HOME"])
    else:
        root = Path.home() / ".local" / "share"
    return root / "TetrisMinimal" / "highscore.txt"
