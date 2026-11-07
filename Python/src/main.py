"""Start the standalone minimalist Tetris application."""

from __future__ import annotations

import time
from pathlib import Path

import pygame

from .audio import Audio
from .config import FPS, MIN_WINDOW_SIZE, WINDOW_SIZE, high_score_path
from .effects import Effects
from .game import Game
from .input_handler import InputHandler
from .renderer import Renderer


def load_high_score(path: Path) -> int:
    try:
        return max(0, int(path.read_text(encoding="utf-8").strip()))
    except (OSError, ValueError):
        return 0


def save_high_score(path: Path, score: int) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{score}\n", encoding="utf-8")
    except OSError:
        # The game remains playable if the user's data directory is read-only.
        pass


def _limit_window_size() -> None:
    try:
        from pygame._sdl2.video import Window

        Window.from_display_module().min_size = MIN_WINDOW_SIZE
    except (ImportError, AttributeError, pygame.error):
        pass


def _consume_game_events(game: Game, effects: Effects, audio: Audio) -> None:
    sounds = {
        "move": "move",
        "rotate": "rotate",
        "lock": "lock",
        "soft_drop": "soft_drop",
        "hard_drop": "hard_drop",
        "clear": "clear",
        "tetris": "tetris",
        "level": "level",
        "game_over": "game_over",
    }
    for name, value in game.events:
        if name == "score":
            effects.scored()
        elif name == "clear" and isinstance(value, tuple):
            effects.clear_rows(value)
        sound = sounds.get(name)
        if sound:
            audio.play(sound)
    game.events.clear()


def main() -> int:
    pygame.init()
    pygame.font.init()
    surface = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
    _limit_window_size()
    pygame.display.set_caption("Tetris — Minimal Edition")

    path = high_score_path()
    game = Game(high_score=load_high_score(path))
    effects = Effects()
    audio = Audio()
    renderer = Renderer(surface)
    controls = InputHandler(renderer, audio, effects)
    clock = pygame.time.Clock()
    elapsed = 0.0
    saved_high = game.high_score

    while controls.running:
        dt = clock.tick(FPS) / 1000.0
        elapsed += dt
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.VIDEORESIZE:
                size = (max(MIN_WINDOW_SIZE[0], event.w), max(MIN_WINDOW_SIZE[1], event.h))
                surface = pygame.display.set_mode(size, pygame.RESIZABLE)
                renderer.resize(surface)

        if not controls.process(events, game):
            break
        controls.update(dt, game)
        game.update(dt)
        effects.update(dt)
        _consume_game_events(game, effects, audio)
        if game.high_score > saved_high:
            saved_high = game.high_score
            save_high_score(path, saved_high)

        renderer.draw(game, effects, elapsed, audio.muted)
        pygame.display.flip()

    save_high_score(path, game.high_score)
    audio.close()
    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
