#include "effects.h"
#include <string.h>

void EffectsInit(Effects *effects) { memset(effects, 0, sizeof(*effects)); }

void EffectsClear(Effects *effects, const Board *board, int lines) {
  if (lines <= 0) return;
  effects->flash = 0.22f;
  int rows = lines > 4 ? 4 : lines;
  for (int row = BOARD_HEIGHT - rows; row < BOARD_HEIGHT; ++row) {
    for (int x = 0; x < BOARD_WIDTH; ++x) {
      int cell = board->cells[row][x];
      if (effects->count >= MAX_PARTICLES) continue;
      Particle *p = &effects->particles[effects->count++];
      p->position = (Vector2){(float)x, (float)row};
      p->velocity = (Vector2){(float)GetRandomValue(-5, 5) * 0.4f, (float)GetRandomValue(-10, -2) * 0.35f};
      p->life = p->maxLife = 0.45f + (float)GetRandomValue(0, 60) / 100.0f;
      p->color = cell ? (Color){(unsigned char)(60 + (cell * 31) % 180), (unsigned char)(150 + (cell * 13) % 100), 255, 255}
                      : (Color){80, (unsigned char)(150 + (x * 9) % 100), 255, 255};
    }
  }
}

void EffectsUpdate(Effects *effects, float dt) {
  if (dt > 0.1f) dt = 0.1f;
  effects->pulse += dt;
  if (effects->flash > 0.0f) effects->flash -= dt;
  for (int i = 0; i < effects->count;) {
    Particle *p = &effects->particles[i];
    p->life -= dt;
    if (p->life <= 0.0f) { effects->particles[i] = effects->particles[--effects->count]; continue; }
    p->position.x += p->velocity.x * dt;
    p->position.y += p->velocity.y * dt;
    p->velocity.y += 8.0f * dt;
    ++i;
  }
}
