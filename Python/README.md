# Tetris — Minimal Edition (Python / Pygame)

A complete standalone Pygame Tetris game with a calm warm-neutral palette, generous spacing, crisp geometric pieces, subtle transitions, soft shadows, and synthesized optional audio. Its visual language is intentionally distinct from the C Raylib Neon Arcade implementation.

## Requirements and install

Python 3.10 or newer and pip. Create a virtual environment and install the project dependencies from this directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Python 3.13 and earlier, the requirements install Pygame. On Python 3.14, they install Pygame Community Edition, which provides the same `pygame` import API and current interpreter wheels.

## Run

From `Python/` with the virtual environment activated:

```powershell
python -m src.main
```

## Controls

| Action | Key |
| --- | --- |
| Move left | Left Arrow / A |
| Move right | Right Arrow / D |
| Soft drop | Down Arrow / S |
| Rotate clockwise | Up Arrow / X |
| Rotate counterclockwise | Z |
| Hard drop | Space |
| Hold / swap | C / Shift |
| Pause / resume | P / Escape |
| Restart | R |
| Toggle audio | M |

## Gameplay

The core rules mirror the C version: 10 by 20 board, all seven tetrominoes, seven-bag generation, five-piece preview, one hold per falling piece, ghost landing position, SRS wall kicks, and time-based gravity. Single, double, triple, and four-line clears are worth 100, 300, 500, and 800 points times the current level. Soft drops award 1 point per cell; hard drops award 2. Levels increase per 10 lines and gravity bottoms out at a 0.05 second interval. Score, level, high score, and lines are shown in-game.

The high score is saved in the user's app data folder (`%APPDATA%/TetrisMinimal/highscore.txt` on Windows, `$XDG_DATA_HOME/TetrisMinimal/highscore.txt` when configured, or `~/.local/share/TetrisMinimal/highscore.txt`). Sound effects are synthesized and loaded in memory. Audio setup failure leaves the game playable and silent. Press M to mute.

## Tests

Tests do not initialize a graphics or audio device:

```powershell
python -m pytest
```

They cover all piece shapes and rotations, boundaries and collisions, hidden spawn/top-out, board locking and one-to-four line clears, SRS kicks, movement, ghost landing, gravity, soft/hard-drop points, line scoring, level progression, seven-bag distribution, hold restrictions, pause, restart, and game-over.

## Assets and limitations

The game uses system sans-serif fonts and original synthesized sound effects. It requires no bundled font, image, or audio assets and adds no dependency beyond Pygame and pytest. SRS lock delay and T-spin/combo scoring are not implemented; line-clear scoring follows the common C implementation.
