# Tetris: Neon Arcade (C / Raylib)

A standalone, native C11 Tetris game with a dark arcade presentation, neon tetrominoes, CRT scanlines, particles, synthesized sound effects, and headless gameplay tests. The game uses Raylib for windowing, drawing, keyboard input, and audio. Gameplay logic is kept in a separate library and does not depend on Raylib.

## Requirements

- Windows 10/11, Linux, or macOS
- CMake 3.20 or newer
- A C11 compiler (GCC, Clang, or MSVC)
- Git and network access on the first configure if Raylib is not installed

Raylib 5.5 is fetched by CMake when no installed Raylib package is found. No audio, font, image, or other asset downloads are required. The sound effects are synthesized in memory at startup. Raylib's upstream license is zlib/libpng; see [Raylib's license](https://github.com/raysan5/raylib/blob/5.5/LICENSE).

## Build and run

From the `C/` directory:

```powershell
cmake -S . -B build
cmake --build build --config Release
```

On Windows with MinGW, tell CMake where to find GCC and `mingw32-make` if they are not on `PATH`:

```powershell
cmake -S . -B build -G "MinGW Makefiles" `
  -DCMAKE_C_COMPILER="C:/Program Files/CodeBlocks/MinGW/bin/gcc.exe" `
  -DCMAKE_MAKE_PROGRAM="C:/Program Files/CodeBlocks/MinGW/bin/mingw32-make.exe"
cmake --build build --parallel
```

In this workspace, CMake and GCC are bundled with Code::Blocks. From the repository root, these commands build the Raylib executable and headless tests with those exact tools:

```powershell
& 'C:\Program Files\CodeBlocks\MinGW\bin\cmake.exe' -S C -B C/build-raylib -G 'MinGW Makefiles' `
  '-DCMAKE_C_COMPILER=C:/Program Files/CodeBlocks/MinGW/bin/gcc.exe' `
  '-DCMAKE_MAKE_PROGRAM=C:/Program Files/CodeBlocks/MinGW/bin/mingw32-make.exe' `
  -DTETRIS_FETCH_RAYLIB=ON -DTETRIS_BUILD_TESTS=ON
& 'C:\Program Files\CodeBlocks\MinGW\bin\cmake.exe' --build C/build-raylib --parallel
& 'C:\Program Files\CodeBlocks\MinGW\bin\ctest.exe' --test-dir C/build-raylib --output-on-failure
& '.\C\build-raylib\c_tetris.exe'
```

Run `build/c_tetris.exe` on Windows, or `./build/c_tetris` on Linux/macOS when building from inside `C/`. If Raylib is already installed and CMake can locate it, no network is needed. To disable the automatic fetch and build only the core tests, pass `-DTETRIS_FETCH_RAYLIB=OFF`.

### Install the toolchain on Windows

Install CMake and a C compiler if they are missing. For example, with Windows Package Manager:

```powershell
winget install --id Kitware.CMake --exact
winget install --id MSYS2.MSYS2 --exact
```

Then open the **MSYS2 UCRT64** terminal and install GCC, CMake, Git, and Raylib:

```sh
pacman -Syu
pacman -S --needed mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-git mingw-w64-ucrt-x86_64-raylib
```

Add `C:\msys64\ucrt64\bin` to `PATH`, open a new PowerShell, and use the standard CMake commands above. Alternatively, leave `TETRIS_FETCH_RAYLIB` enabled and CMake will build Raylib from source.

## Controls

| Key | Action |
| --- | --- |
| Left / Right | Move horizontally (DAS/ARR repeat) |
| Down | Soft drop (1 point per cell) |
| Space | Hard drop (2 points per cell) |
| X / Up | Rotate clockwise |
| Z | Rotate counterclockwise |
| C | Hold or swap the current piece once per drop |
| P / Escape | Pause or resume |
| M | Toggle synthesized sound |
| Enter | Start, resume, or restart |

## Gameplay and persistence

The board is 10 by 20 and stores each occupied cell's piece type. Seven-bag generation, a five-piece next queue and preview, SRS wall kicks, ghost landing indicator, hold, scoring, and gravity are implemented in `tetris_core`. Gravity is time-based and capped at 20 drops per second. Line scores are 100/300/500/800 multiplied by the current level, and levels advance for each ten lines.

The high score is stored as a small text file in `%APPDATA%/C-Tetris/highscore.txt` on Windows, `$XDG_DATA_HOME/C-Tetris/highscore.txt` (or `~/.local/share/C-Tetris/highscore.txt`) on Linux, and the current directory as a fallback.

## Tests

The gameplay tests have no graphics or audio dependency. Run these commands from inside `C/`:

```powershell
cmake -S . -B build -DTETRIS_FETCH_RAYLIB=OFF -DTETRIS_BUILD_TESTS=ON
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

They cover tetromino shape cell counts, movement and collision, rotations and a wall kick, locking/top-out, one through four line clears, scoring, level changes and gravity cap, seven-bag contents, hold restrictions, and pause state.

## Known limits

- The visuals use Raylib's built-in font so the project has no bundled font asset.
- Lock delay and advanced T-spin/combo/back-to-back scoring are not included; the requested standard line-clear scoring is used.
- Sound is generated procedurally and can be disabled with `M`; it does not use external licensed audio files.
