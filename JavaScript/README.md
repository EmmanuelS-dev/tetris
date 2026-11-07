# Tetris — Canvas Edition (JavaScript)

A self-contained browser implementation with a warm, restrained visual style. It uses native Canvas and browser APIs; no build step or third-party package is required.

## Run

Open `index.html` in a modern browser, or serve this directory locally:

```sh
node server.js
```

Then visit `http://localhost:8000`. Tests use Node's built-in test runner:

```sh
node --test
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

The 10×20 board, seven-bag randomizer, SRS kicks, hold restriction, five-piece queue, ghost projection, score table (100/300/500/800 × level), drop points, 10-line levels and gravity interval match the C and Python editions. High score is saved in browser local storage. Sound is synthesized and starts muted.
