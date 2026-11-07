"""Lightweight visual particles and UI animation timers."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    duration: float
    color: tuple[int, int, int]


class Effects:
    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)
        self.particles: list[Particle] = []
        self.score_pulse = 0.0
        self.screen_fade = 0.0

    def clear_rows(self, rows: tuple[int, ...]) -> None:
        for row in rows:
            for col in range(10):
                for _ in range(2):
                    duration = self.random.uniform(0.3, 0.7)
                    self.particles.append(
                        Particle(
                            col + 0.5,
                            row + 0.5,
                            self.random.uniform(-2.8, 2.8),
                            self.random.uniform(-4.5, -1.0),
                            duration,
                            duration,
                            self.random.choice(
                                ((91, 174, 186), (151, 123, 178), (113, 166, 132), (220, 177, 91))
                            ),
                        )
                    )
        del self.particles[:-180]

    def scored(self) -> None:
        self.score_pulse = 0.28

    def update(self, dt: float) -> None:
        dt = max(0.0, min(dt, 0.1))
        self.score_pulse = max(0.0, self.score_pulse - dt)
        self.screen_fade = min(0.25, self.screen_fade + dt)
        alive: list[Particle] = []
        for particle in self.particles:
            particle.life -= dt
            if particle.life <= 0:
                continue
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            particle.vy += 7.0 * dt
            alive.append(particle)
        self.particles = alive
