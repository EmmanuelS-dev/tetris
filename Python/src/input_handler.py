"""Keyboard and mouse handling, including frame-independent key repeat."""

from __future__ import annotations

import pygame

from .audio import Audio
from .effects import Effects
from .game import Game, Screen
from .renderer import Renderer

DAS = 0.16
ARR = 0.045


class InputHandler:
    def __init__(self, renderer: Renderer, audio: Audio, effects: Effects) -> None:
        self.renderer = renderer
        self.audio = audio
        self.effects = effects
        self.down_keys: set[int] = set()
        self.horizontal_timer = 0.0
        self.soft_timer = 0.0
        self.last_horizontal = 0
        self.running = True

    @staticmethod
    def _horizontal_key(key: int) -> int:
        if key in (pygame.K_LEFT, pygame.K_a):
            return -1
        if key in (pygame.K_RIGHT, pygame.K_d):
            return 1
        return 0

    @staticmethod
    def _soft_key(key: int) -> bool:
        return key in (pygame.K_DOWN, pygame.K_s)

    def _active_horizontal(self) -> int:
        has_left = any(key in self.down_keys for key in (pygame.K_LEFT, pygame.K_a))
        has_right = any(key in self.down_keys for key in (pygame.K_RIGHT, pygame.K_d))
        if has_left and has_right:
            return self.last_horizontal
        if has_left:
            return -1
        if has_right:
            return 1
        return 0

    def process(self, events: list[pygame.event.Event], game: Game) -> bool:
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.WINDOWFOCUSLOST:
                self.down_keys.clear()
                self.horizontal_timer = self.soft_timer = 0.0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._click(event.pos, game)
            elif event.type == pygame.KEYDOWN:
                self._key_down(event.key, game)
            elif event.type == pygame.KEYUP:
                self._key_up(event.key)
        return self.running

    def _click(self, position: tuple[int, int], game: Game) -> None:
        buttons = self.renderer.buttons_for(game)
        name = next((key for key, rect in buttons.items() if rect.collidepoint(position)), None)
        if game.state == Screen.MENU:
            if name == "play":
                self._start(game)
            elif name == "controls":
                game.state = Screen.CONTROLS
            elif name == "quit":
                self.running = False
        elif game.state == Screen.CONTROLS and name == "back":
            game.state = Screen.MENU
        elif game.state == Screen.PAUSED:
            if name == "resume":
                game.toggle_pause()
            elif name == "restart":
                self._start(game)
            elif name == "menu":
                game.state = Screen.MENU
        elif game.state == Screen.GAME_OVER:
            if name == "restart":
                self._start(game)
            elif name == "menu":
                game.state = Screen.MENU

    def _key_down(self, key: int, game: Game) -> None:
        if key == pygame.K_m:
            self.audio.toggle()
            return
        if game.state == Screen.MENU:
            if key in (pygame.K_DOWN, pygame.K_s):
                self.renderer.menu_selection = (self.renderer.menu_selection + 1) % 3
            elif key in (pygame.K_UP, pygame.K_w):
                self.renderer.menu_selection = (self.renderer.menu_selection - 1) % 3
            elif key in (pygame.K_RETURN, pygame.K_SPACE):
                choice = ("play", "controls", "quit")[self.renderer.menu_selection]
                self._click_choice(choice, game)
            elif key == pygame.K_c:
                game.state = Screen.CONTROLS
            elif key == pygame.K_q:
                self.running = False
            return
        if game.state == Screen.CONTROLS:
            if key in (pygame.K_ESCAPE, pygame.K_RETURN):
                game.state = Screen.MENU
            return
        if game.state == Screen.PAUSED:
            if key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_RETURN):
                game.toggle_pause()
            elif key == pygame.K_r:
                self._start(game)
            elif key == pygame.K_m:
                self.audio.toggle()
            return
        if game.state == Screen.GAME_OVER:
            if key in (pygame.K_RETURN, pygame.K_r):
                self._start(game)
            elif key == pygame.K_ESCAPE:
                game.state = Screen.MENU
            return
        if game.state != Screen.PLAYING:
            return

        if key in (pygame.K_ESCAPE, pygame.K_p):
            game.toggle_pause()
            self.down_keys.clear()
            return
        if key == pygame.K_r:
            self._start(game)
            return
        if key in (pygame.K_UP, pygame.K_x):
            game.rotate(1)
            return
        if key == pygame.K_z:
            game.rotate(-1)
            return
        if key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
            game.hold_piece()
            return
        if key == pygame.K_SPACE:
            game.hard_drop()
            return

        direction = self._horizontal_key(key)
        if direction:
            if key not in self.down_keys:
                self.down_keys.add(key)
                self.last_horizontal = direction
                game.move(direction, 0)
                self.horizontal_timer = DAS
            return
        if self._soft_key(key) and key not in self.down_keys:
            self.down_keys.add(key)
            game.soft_drop()
            self.soft_timer = ARR

    def _click_choice(self, choice: str, game: Game) -> None:
        if choice == "play":
            self._start(game)
        elif choice == "controls":
            game.state = Screen.CONTROLS
        else:
            self.running = False

    def _key_up(self, key: int) -> None:
        if key in self.down_keys:
            self.down_keys.remove(key)
        if self._horizontal_key(key):
            direction = self._active_horizontal()
            self.last_horizontal = direction
            self.horizontal_timer = DAS if direction else 0.0
        if self._soft_key(key) and not any(self._soft_key(held) for held in self.down_keys):
            self.soft_timer = 0.0

    def update(self, dt: float, game: Game) -> None:
        if game.state != Screen.PLAYING:
            return
        direction = self._active_horizontal()
        if direction:
            self.horizontal_timer -= dt
            while self.horizontal_timer <= 0:
                game.move(direction, 0)
                self.horizontal_timer += ARR
        if any(self._soft_key(key) for key in self.down_keys):
            self.soft_timer -= dt
            while self.soft_timer <= 0:
                game.soft_drop()
                self.soft_timer += ARR

    def _start(self, game: Game) -> None:
        game.start_game()
        self.down_keys.clear()
        self.horizontal_timer = self.soft_timer = 0.0
