"""Responsive minimalist Pygame presentation layer."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from .config import (
    ACCENT,
    ACCENT_SOFT,
    BACKGROUND_BOTTOM,
    BACKGROUND_TOP,
    BOARD_HEIGHT,
    BOARD_SURFACE,
    BOARD_WIDTH,
    GRID,
    INK,
    MUTED,
    NEXT_QUEUE_SIZE,
    PIECE_COLORS,
    SHADOW,
    SURFACE,
)
from .effects import Effects
from .game import Game, Screen
from .tetromino import Piece, local_cells


@dataclass(frozen=True)
class Layout:
    width: int
    height: int
    cell: int
    board_x: int
    board_y: int
    board_width: int
    board_height: int
    left_x: int
    right_x: int
    panel_width: int


class Renderer:
    def __init__(self, surface: pygame.Surface) -> None:
        self.surface = surface
        self.font_cache: dict[tuple[int, bool], pygame.font.Font] = {}
        self.last_screen: Screen | None = None
        self.transition_time = 0.25
        self.score_time = 0.0
        self.last_score: int | None = None
        self.buttons: dict[str, pygame.Rect] = {}
        self.menu_selection = 0

    def resize(self, surface: pygame.Surface) -> None:
        self.surface = surface

    def layout(self) -> Layout:
        width, height = self.surface.get_size()
        cell = max(18, min(34, (height - 160) // BOARD_HEIGHT, (width - 400) // BOARD_WIDTH))
        board_width, board_height = cell * BOARD_WIDTH, cell * BOARD_HEIGHT
        board_x = (width - board_width) // 2
        board_y = (height - board_height) // 2 + 14
        panel_width = min(194, max(150, (width - board_width - 96) // 2))
        return Layout(
            width, height, cell, board_x, board_y, board_width, board_height,
            board_x - panel_width - 26, board_x + board_width + 26, panel_width,
        )

    def _font(self, size: int, bold: bool = False) -> pygame.font.Font:
        key = (max(10, size), bold)
        if key not in self.font_cache:
            self.font_cache[key] = pygame.font.SysFont(("segoeui", "aptos", "arial"), key[0], bold=bold)
        return self.font_cache[key]

    def _text(
        self,
        text: str,
        x: int,
        y: int,
        size: int,
        color: tuple[int, int, int] = INK,
        *,
        bold: bool = False,
        center: bool = False,
    ) -> pygame.Rect:
        image = self._font(size, bold).render(text, True, color)
        rect = image.get_rect(midtop=(x, y) if center else image.get_rect(topleft=(x, y)).topleft)
        self.surface.blit(image, rect)
        return rect

    def _panel(self, rect: pygame.Rect, radius: int = 14, color: tuple[int, int, int] = SURFACE) -> None:
        shadow_surface = pygame.Surface((rect.width + 10, rect.height + 12), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, SHADOW, shadow_surface.get_rect().inflate(-8, -10), border_radius=radius + 2)
        self.surface.blit(shadow_surface, (rect.x - 1, rect.y + 5))
        pygame.draw.rect(self.surface, color, rect, border_radius=radius)
        pygame.draw.rect(self.surface, (232, 234, 230), rect, width=1, border_radius=radius)

    def buttons_for(self, game: Game) -> dict[str, pygame.Rect]:
        width, height = self.surface.get_size()
        center_x = width // 2
        buttons: dict[str, pygame.Rect] = {}
        if game.state == Screen.MENU:
            start_y = height // 2 - 8
            buttons = {
                "play": pygame.Rect(center_x - 124, start_y, 248, 52),
                "controls": pygame.Rect(center_x - 124, start_y + 68, 248, 52),
                "quit": pygame.Rect(center_x - 124, start_y + 136, 248, 52),
            }
        elif game.state == Screen.CONTROLS:
            buttons = {"back": pygame.Rect(center_x - 124, height - 100, 248, 52)}
        elif game.state == Screen.PAUSED:
            start_y = height // 2 - 4
            buttons = {
                "resume": pygame.Rect(center_x - 124, start_y, 248, 50),
                "restart": pygame.Rect(center_x - 124, start_y + 64, 248, 50),
                "menu": pygame.Rect(center_x - 124, start_y + 128, 248, 50),
            }
        elif game.state == Screen.GAME_OVER:
            start_y = height // 2 + 52
            buttons = {
                "restart": pygame.Rect(center_x - 124, start_y, 248, 50),
                "menu": pygame.Rect(center_x - 124, start_y + 64, 248, 50),
            }
        return buttons

    def _draw_button(
        self, name: str, label: str, rect: pygame.Rect, mouse: tuple[int, int], selected: bool = False
    ) -> None:
        hover = rect.collidepoint(mouse) or selected
        fill = ACCENT if hover else SURFACE
        text_color = (255, 255, 255) if hover else INK
        pygame.draw.rect(self.surface, (37, 49, 54, 22), rect.move(0, 4), border_radius=12)
        pygame.draw.rect(self.surface, fill, rect, border_radius=12)
        pygame.draw.rect(self.surface, ACCENT if hover else (222, 225, 220), rect, width=1, border_radius=12)
        self._text(label, rect.centerx, rect.y + 15, 16, text_color, bold=True, center=True)
        self.buttons[name] = rect

    def _draw_background(self, elapsed: float) -> None:
        width, height = self.surface.get_size()
        for y in range(height):
            t = y / max(1, height - 1)
            color = tuple(round(a + (b - a) * t) for a, b in zip(BACKGROUND_TOP, BACKGROUND_BOTTOM))
            pygame.draw.line(self.surface, color, (0, y), (width, y))
        drift = int(math.sin(elapsed * 0.25) * 16)
        pygame.draw.circle(self.surface, (244, 243, 237), (-90 + drift, height // 3), 220)
        pygame.draw.circle(self.surface, (242, 244, 239), (width + 85 - drift, height * 2 // 3), 180)

    def draw(self, game: Game, effects: Effects, elapsed: float, muted: bool) -> None:
        if game.state != self.last_screen:
            self.last_screen = game.state
            self.transition_time = 0.0
        self.transition_time = min(0.25, self.transition_time + 1 / 60)
        if self.last_score != game.score:
            if self.last_score is not None:
                self.score_time = 0.28
            self.last_score = game.score
        self.score_time = max(0.0, self.score_time - 1 / 60)
        self._draw_background(elapsed)
        if game.state == Screen.MENU:
            self._draw_menu(game, elapsed)
        elif game.state == Screen.CONTROLS:
            self._draw_controls(game)
        else:
            self._draw_game(game, effects, muted)
            if game.state in (Screen.PAUSED, Screen.GAME_OVER):
                self._draw_overlay(game)
        if self.transition_time < 0.25:
            veil = pygame.Surface(self.surface.get_size(), pygame.SRCALPHA)
            veil.fill((248, 247, 243, int((0.25 - self.transition_time) * 74)))
            self.surface.blit(veil, (0, 0))

    def _draw_menu(self, game: Game, elapsed: float) -> None:
        width, height = self.surface.get_size()
        center = width // 2
        pygame.draw.circle(self.surface, (234, 239, 234), (int(width * 0.18), int(height * 0.30 + math.sin(elapsed) * 8)), 52, 1)
        pygame.draw.circle(self.surface, (234, 239, 234), (int(width * 0.82), int(height * 0.68 + math.cos(elapsed * 0.8) * 10)), 72, 1)
        self._text("T E T R I S", center, height // 4, 48, INK, bold=True, center=True)
        self._text("A QUIET GAME OF SPATIAL RHYTHM", center, height // 4 + 62, 13, MUTED, center=True)
        mouse = pygame.mouse.get_pos()
        self.buttons = self.buttons_for(game)
        for index, (name, label) in enumerate((("play", "PLAY"), ("controls", "CONTROLS"), ("quit", "QUIT"))):
            self._draw_button(name, label, self.buttons[name], mouse, selected=index == self.menu_selection)
        self._text("←  →  MOVE     ↓  SOFT DROP     SPACE  DROP", center, height - 57, 12, MUTED, center=True)

    def _draw_controls(self, game: Game) -> None:
        width, height = self.surface.get_size()
        center = width // 2
        self._text("CONTROLS", center, 64, 34, INK, bold=True, center=True)
        rows = (
            ("← / A", "Move left"), ("→ / D", "Move right"), ("↓ / S", "Soft drop"),
            ("↑ / X", "Rotate clockwise"), ("Z", "Rotate counterclockwise"),
            ("SPACE", "Hard drop"), ("C / SHIFT", "Hold piece"),
            ("P / ESC", "Pause"), ("R", "Restart"), ("M", "Toggle sound"),
        )
        origin_y = max(150, height // 2 - 190)
        for i, (key, action) in enumerate(rows):
            y = origin_y + i * 34
            self._text(key, center - 190, y, 15, ACCENT, bold=True)
            self._text(action, center - 28, y, 15, INK)
        self.buttons = self.buttons_for(game)
        self._draw_button("back", "BACK", self.buttons["back"], pygame.mouse.get_pos())

    def _draw_game(self, game: Game, effects: Effects, muted: bool) -> None:
        layout = self.layout()
        cell, bx, by = layout.cell, layout.board_x, layout.board_y
        self._text("TETRIS", layout.width // 2, 22, 17, INK, bold=True, center=True)
        self._text("MINIMAL EDITION", layout.width // 2, 47, 10, MUTED, center=True)
        board_rect = pygame.Rect(bx - 8, by - 8, layout.board_width + 16, layout.board_height + 16)
        self._panel(board_rect, 15)
        pygame.draw.rect(self.surface, BOARD_SURFACE, (bx, by, layout.board_width, layout.board_height), border_radius=5)
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                rect = pygame.Rect(bx + x * cell, by + y * cell, cell, cell)
                pygame.draw.rect(self.surface, GRID, rect, width=1)
                kind = game.board.grid[y][x]
                if kind:
                    self._draw_block(rect, PIECE_COLORS[kind])
        if game.state in (Screen.PLAYING, Screen.PAUSED):
            self._draw_piece(game.ghost_piece(), bx, by, cell, ghost=True)
            self._draw_piece(game.active, bx, by, cell)
        self._draw_particles(effects, bx, by, cell)
        self._draw_side_panels(game, layout, muted)

    def _draw_side_panels(self, game: Game, layout: Layout, muted: bool) -> None:
        panel_w = layout.panel_width
        left = layout.left_x
        right = layout.right_x
        top = layout.board_y + 2
        self._text("HOLD", left, top, 12, MUTED, bold=True)
        hold_rect = pygame.Rect(left, top + 23, panel_w, 106)
        self._panel(hold_rect, 12)
        if game.held:
            self._draw_preview(game.held, hold_rect)
        self._text("C / SHIFT  ·  Hold once per piece", left, top + 148, 11, MUTED)
        self._text("P / ESC  ·  Pause", left, top + 172, 11, MUTED)
        self._text("R  ·  Restart", left, top + 196, 11, MUTED)

        self._text("NEXT", right, top, 12, MUTED, bold=True)
        next_rect = pygame.Rect(right, top + 23, panel_w, 282)
        self._panel(next_rect, 12)
        slot_height = 48
        for index, kind in enumerate(game.next_queue[:NEXT_QUEUE_SIZE]):
            slot = pygame.Rect(right + 8, top + 29 + index * slot_height, panel_w - 16, slot_height)
            self._draw_preview(kind, slot)

        stats = pygame.Rect(right, top + 320, panel_w, 220)
        self._panel(stats, 12)
        score_size = 29 if self.score_time <= 0 else round(29 + 3 * self.score_time / 0.28)
        self._text("SCORE", right + 16, stats.y + 18, 10, MUTED, bold=True)
        self._text(f"{game.score:,}", right + 16, stats.y + 38, score_size, INK, bold=True)
        self._text("BEST", right + 16, stats.y + 91, 10, MUTED, bold=True)
        self._text(f"{game.high_score:,}", right + 16, stats.y + 108, 16, ACCENT, bold=True)
        divider_y = stats.y + 144
        pygame.draw.line(self.surface, GRID, (right + 16, divider_y), (right + panel_w - 16, divider_y), 1)
        self._text("LEVEL", right + 16, stats.y + 160, 9, MUTED, bold=True)
        self._text(str(game.level), right + 16, stats.y + 177, 18, INK, bold=True)
        self._text("LINES", right + panel_w // 2 + 4, stats.y + 160, 9, MUTED, bold=True)
        self._text(str(game.lines), right + panel_w // 2 + 4, stats.y + 177, 18, INK, bold=True)
        self._text("SOUND  ·  " + ("OFF" if muted else "ON") + "  [M]", right, stats.bottom + 14, 10, MUTED)

    def _draw_preview(self, kind: str, bounds: pygame.Rect) -> None:
        cells = local_cells(kind)
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        mini = max(10, min(17, (bounds.width - 22) // (max_x - min_x + 1), (bounds.height - 8) // (max_y - min_y + 1)))
        piece_w, piece_h = (max_x - min_x + 1) * mini, (max_y - min_y + 1) * mini
        start_x = bounds.centerx - piece_w // 2
        start_y = bounds.centery - piece_h // 2
        for x, y in cells:
            self._draw_block(
                pygame.Rect(start_x + (x - min_x) * mini, start_y + (y - min_y) * mini, mini, mini),
                PIECE_COLORS[kind],
            )

    def _draw_block(self, rect: pygame.Rect, color: tuple[int, int, int], ghost: bool = False) -> None:
        inset = max(1, rect.width // 12)
        block = rect.inflate(-inset * 2, -inset * 2)
        if ghost:
            layer = pygame.Surface(block.size, pygame.SRCALPHA)
            pygame.draw.rect(layer, (*color, 48), layer.get_rect(), border_radius=max(3, inset * 2))
            pygame.draw.rect(layer, (*color, 150), layer.get_rect(), width=1, border_radius=max(3, inset * 2))
            self.surface.blit(layer, block.topleft)
            return
        pygame.draw.rect(self.surface, tuple(max(0, c - 25) for c in color), block.move(0, 2), border_radius=max(4, inset * 3))
        pygame.draw.rect(self.surface, color, block, border_radius=max(4, inset * 3))
        if block.height >= 14:
            highlight = tuple(min(255, c + 28) for c in color)
            pygame.draw.line(self.surface, highlight, (block.x + 5, block.y + 3), (block.right - 5, block.y + 3), 1)

    def _draw_piece(self, piece: Piece, board_x: int, board_y: int, cell: int, ghost: bool = False) -> None:
        color = PIECE_COLORS[piece.kind]
        for x, y in local_cells(piece.kind, piece.rotation):
            gx, gy = piece.x + x, piece.y + y
            if gy < 0:
                continue
            rect = pygame.Rect(board_x + gx * cell, board_y + gy * cell, cell, cell)
            self._draw_block(rect, color, ghost=ghost)

    def _draw_particles(self, effects: Effects, board_x: int, board_y: int, cell: int) -> None:
        for particle in effects.particles:
            alpha = max(0, min(255, round(255 * particle.life / particle.duration)))
            radius = max(1, round(2 + 2 * alpha / 255))
            layer = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(layer, (*particle.color, alpha), (radius, radius), radius)
            self.surface.blit(layer, (board_x + int(particle.x * cell) - radius, board_y + int(particle.y * cell) - radius))

    def _draw_overlay(self, game: Game) -> None:
        width, height = self.surface.get_size()
        veil = pygame.Surface((width, height), pygame.SRCALPHA)
        veil.fill((37, 43, 46, 155))
        self.surface.blit(veil, (0, 0))
        panel = pygame.Rect(width // 2 - 188, height // 2 - 168, 376, 410 if game.state == Screen.GAME_OVER else 350)
        self._panel(panel, 18)
        if game.state == Screen.PAUSED:
            self._text("PAUSED", width // 2, panel.y + 43, 32, INK, bold=True, center=True)
            self._text("Take your time.", width // 2, panel.y + 91, 14, MUTED, center=True)
        else:
            self._text("GAME OVER", width // 2, panel.y + 35, 29, INK, bold=True, center=True)
            self._text("A good run. Ready for another?", width // 2, panel.y + 79, 13, MUTED, center=True)
            self._text("FINAL SCORE", width // 2, panel.y + 125, 10, MUTED, bold=True, center=True)
            self._text(f"{game.score:,}", width // 2, panel.y + 145, 30, INK, bold=True, center=True)
            self._text(f"BEST  {game.high_score:,}", width // 2, panel.y + 190, 12, ACCENT, bold=True, center=True)
        self.buttons = self.buttons_for(game)
        mouse = pygame.mouse.get_pos()
        labels = (("resume", "RESUME"), ("restart", "RESTART"), ("menu", "MAIN MENU")) if game.state == Screen.PAUSED else (("restart", "RESTART"), ("menu", "MAIN MENU"))
        for name, label in labels:
            self._draw_button(name, label, self.buttons[name], mouse)

