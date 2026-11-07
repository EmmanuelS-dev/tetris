#ifndef TETRIS_EFFECTS_H
#define TETRIS_EFFECTS_H
#include "board.h"
#include <raylib.h>
#define MAX_PARTICLES 160
typedef struct { Vector2 position; Vector2 velocity; float life; float maxLife; Color color; } Particle;
typedef struct { Particle particles[MAX_PARTICLES]; int count; float pulse; float flash; } Effects;
void EffectsInit(Effects *effects);
void EffectsClear(Effects *effects, const Board *board, int lines);
void EffectsUpdate(Effects *effects, float dt);
#endif
