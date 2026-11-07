"""Optional synthesized sound effects; the game is silent if audio is unavailable."""

from __future__ import annotations

import math
from array import array

import pygame


class Audio:
    _FREQUENCIES = {
        "move": (340, 0.035),
        "soft_drop": (230, 0.035),
        "rotate": (510, 0.055),
        "lock": (160, 0.075),
        "hard_drop": (115, 0.13),
        "clear": (680, 0.16),
        "tetris": (880, 0.28),
        "level": (760, 0.19),
        "game_over": (95, 0.4),
    }

    def __init__(self) -> None:
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        self.available = False
        self.muted = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=256)
            for name, (frequency, duration) in self._FREQUENCIES.items():
                self.sounds[name] = pygame.mixer.Sound(buffer=self._tone(frequency, duration))
                self.sounds[name].set_volume(0.14)
            self.available = True
        except pygame.error:
            self.sounds.clear()

    @staticmethod
    def _tone(frequency: float, duration: float) -> bytes:
        sample_rate = 22050
        count = int(sample_rate * duration)
        samples = array("h")
        for index in range(count):
            envelope = 1.0 - index / max(1, count)
            value = math.sin(2.0 * math.pi * frequency * index / sample_rate) * envelope * 6000
            samples.append(int(value))
        if samples.itemsize != 2:
            raise RuntimeError("This platform does not use 16-bit array samples")
        return samples.tobytes()

    def play(self, name: str) -> None:
        if self.available and not self.muted and name in self.sounds:
            self.sounds[name].play()

    def toggle(self) -> None:
        self.muted = not self.muted

    def close(self) -> None:
        if self.available and pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.quit()
        self.available = False
