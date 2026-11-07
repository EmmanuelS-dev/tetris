# Tetris — Stillwater (Java / Swing)

A standalone Java 17+ desktop edition. Java Swing provides the resizable window and drawing surface; the game rules are graphics independent and have no third-party dependencies.

## Build and run

From `Java/`:

```sh
javac -d out src/tetris/*.java
java -cp out tetris.Main
```

## Core checks

```sh
javac -d out src/tetris/*.java tests/tetris/GameEngineTest.java
java -ea -cp out tetris.GameEngineTest
```

## Controls

| Action | Keys |
| --- | --- |
| Move | Left / A, Right / D |
| Soft drop | Down / S |
| Rotate | Up / X clockwise, Z counterclockwise |
| Hard drop | Space |
| Hold | C / Shift |
| Pause / resume | P / Escape |
| Restart | R |
| Sound toggle | M |
| Main menu / quit | Q (pause/game over returns to menu; menu exits) |

The game follows the shared 10×20 board, seven-bag, five-piece queue, SRS kicks, hold, ghost, score values, 10-line levels, and capped time-based gravity. Best score persists through Java Preferences. Short synthesized effects can be toggled with M. There are no external assets or libraries.
