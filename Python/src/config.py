from __future__ import annotations
import os
from pathlib import Path

WIDTH, HEIGHT = 10, 20
QUEUE_SIZE = 5
FPS = 60
WINDOW_SIZE = (1120, 800)
MIN_WINDOW_SIZE = (880, 640)
BG_TOP, BG_BOTTOM = (248, 247, 243), (239, 239, 234)
SURFACE, BOARD_SURFACE = (255, 255, 253), (250, 250, 247)
INK, MUTED, GRID = (40, 47, 54), (121, 129, 135), (229, 231, 226)
ACCENT = (51, 132, 119)
COLORS = {"I": (91,174,186), "O": (220,177,91), "T": (151,123,178),
          "S": (113,166,132), "Z": (205,113,112), "J": (103,133,184), "L": (209,145,91)}

def high_score_path() -> Path:
    root = Path(os.environ["APPDATA"]) if os.name == "nt" and os.getenv("APPDATA") else Path(os.getenv("XDG_DATA_HOME", Path.home()/".local"/"share"))
    return root / "TetrisMinimal" / "highscore.txt"
