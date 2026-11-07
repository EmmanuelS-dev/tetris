# Tetris implementations

This repository contains independent language editions of the same Tetris rules. Each implementation keeps its sources, dependencies, build or run instructions, and tests in its own top-level directory.

- [`C/`](C/README.md) — C11 with Raylib, neon retro arcade presentation.
- [`Python/`](Python/README.md) — Python with Pygame, minimalist presentation.
- [`JavaScript/`](JavaScript/README.md) — browser edition with Canvas rendering.
- [`Java/`](Java/README.md) — desktop edition using Java Swing.

The implementations share board dimensions, tetrominoes, seven-bag generation, SRS rotation kicks, hold and preview, scoring, and level progression. Runtime dependencies remain independent.
