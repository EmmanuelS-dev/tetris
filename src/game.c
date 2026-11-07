#include "game.h"
#include <string.h>

static unsigned int RandomNext(Game *game) {
  unsigned int x = game->rng ? game->rng : 0x9e3779b9u;
  x ^= x << 13; x ^= x >> 17; x ^= x << 5; game->rng = x;
  return x;
}

static PieceType DrawPiece(Game *game) {
  if (game->bagIndex >= PIECE_COUNT) {
    for (int i = 0; i < PIECE_COUNT; ++i) game->bag[i] = (PieceType)i;
    for (int i = PIECE_COUNT - 1; i > 0; --i) {
      int j = (int)(RandomNext(game) % (unsigned)(i + 1));
      PieceType swap = game->bag[i]; game->bag[i] = game->bag[j]; game->bag[j] = swap;
    }
    game->bagIndex = 0;
  }
  return game->bag[game->bagIndex++];
}

static void FillQueue(Game *game) { for (int i = 0; i < NEXT_QUEUE_SIZE; ++i) game->queue[i] = DrawPiece(game); }
static Piece SpawnPiece(PieceType type) { Piece piece = {type, 0, 3, -1}; return piece; }

static int SpawnNext(Game *game) {
  PieceType next = game->queue[0];
  memmove(game->queue, game->queue + 1, (NEXT_QUEUE_SIZE - 1) * sizeof(game->queue[0]));
  game->queue[NEXT_QUEUE_SIZE - 1] = DrawPiece(game);
  game->active = SpawnPiece(next);
  game->holdUsed = 0;
  game->gravityTimer = game->lockTimer = 0.0f;
  if (!BoardCanPlace(&game->board, game->active)) { game->screen = GAME_OVER; return 0; }
  return 1;
}

void GameInit(Game *game, unsigned int seed, int highScore) {
  memset(game, 0, sizeof(*game));
  game->rng = seed ? seed : 1u;
  game->highScore = highScore;
  game->held = PIECE_I;
  game->level = 1;
  game->screen = GAME_MENU;
}

void GameStart(Game *game, unsigned int seed) {
  int high = game->highScore;
  memset(game, 0, sizeof(*game));
  game->rng = seed ? seed : 1u;
  game->highScore = high;
  game->held = PIECE_I;
  game->level = 1;
  game->screen = GAME_PLAYING;
  game->bagIndex = PIECE_COUNT;
  FillQueue(game);
  game->active = SpawnPiece(game->queue[0]);
  memmove(game->queue, game->queue + 1, (NEXT_QUEUE_SIZE - 1) * sizeof(game->queue[0]));
  game->queue[NEXT_QUEUE_SIZE - 1] = DrawPiece(game);
}

void GameAddScore(Game *game, int points) {
  if (points <= 0) return;
  game->score += points;
  if (game->score > game->highScore) game->highScore = game->score;
}

int GameMove(Game *game, int dx, int dy) {
  if (game->screen != GAME_PLAYING) return 0;
  Piece candidate = game->active;
  candidate.x += dx; candidate.y += dy;
  if (!BoardCanPlace(&game->board, candidate)) return 0;
  game->active = candidate;
  if (dy > 0) game->lockTimer = 0.0f;
  if (dx != 0) game->lockTimer = 0.0f;
  return 1;
}

int GameSoftDrop(Game *game) {
  if (!GameMove(game, 0, 1)) return 0;
  GameAddScore(game, 1);
  return 1;
}

static const int JLSTZ_KICKS[8][5][2] = {
  {{0,0},{-1,0},{-1,-1},{0,2},{-1,2}}, {{0,0},{1,0},{1,1},{0,-2},{1,-2}},
  {{0,0},{1,0},{1,1},{0,-2},{1,-2}}, {{0,0},{-1,0},{-1,-1},{0,2},{-1,2}},
  {{0,0},{1,0},{1,-1},{0,2},{1,2}}, {{0,0},{-1,0},{-1,1},{0,-2},{-1,-2}},
  {{0,0},{-1,0},{-1,1},{0,-2},{-1,-2}}, {{0,0},{1,0},{1,-1},{0,2},{1,2}}
};
static const int I_KICKS[8][5][2] = {
  {{0,0},{-2,0},{1,0},{-2,-1},{1,2}}, {{0,0},{-1,0},{2,0},{-1,2},{2,-1}},
  {{0,0},{-1,0},{2,0},{-1,2},{2,-1}}, {{0,0},{2,0},{-1,0},{2,1},{-1,-2}},
  {{0,0},{2,0},{-1,0},{2,1},{-1,-2}}, {{0,0},{1,0},{-2,0},{1,-2},{-2,1}},
  {{0,0},{1,0},{-2,0},{1,-2},{-2,1}}, {{0,0},{-2,0},{1,0},{-2,-1},{1,2}}
};

int GameRotate(Game *game, int direction) {
  if (game->screen != GAME_PLAYING || direction == 0) return 0;
  Piece candidate = game->active;
  int from = candidate.rotation, to = (from + (direction > 0 ? 1 : 3)) % 4;
  candidate.rotation = to;
  int transition = from * 2 + (direction > 0 ? 0 : 1);
  const int (*kicks)[2] = candidate.type == PIECE_I ? I_KICKS[transition] : JLSTZ_KICKS[transition];
  if (candidate.type == PIECE_O) return 1;
  for (int i = 0; i < 5; ++i) {
    candidate.x = game->active.x + kicks[i][0];
    candidate.y = game->active.y + kicks[i][1];
    if (BoardCanPlace(&game->board, candidate)) { game->active = candidate; game->lockTimer = 0.0f; return 1; }
  }
  return 0;
}

int GameLockPiece(Game *game) {
  if (game->screen != GAME_PLAYING) return 0;
  int topOut = BoardLock(&game->board, game->active);
  if (topOut < 0) { game->screen = GAME_OVER; return 0; }
  ++game->lockCount;
  if (topOut) { game->screen = GAME_OVER; return 0; }
  int cleared = BoardClearLines(&game->board);
  static const int scores[] = {0, 100, 300, 500, 800};
  if (cleared > 0) GameAddScore(game, scores[cleared > 4 ? 4 : cleared] * game->level);
  int oldLevel = game->level;
  game->lines += cleared;
  game->level = 1 + game->lines / 10;
  if (game->level > oldLevel) { game->gravityTimer = 0.0f; }
  SpawnNext(game);
  return cleared;
}

int GameHardDrop(Game *game) {
  if (game->screen != GAME_PLAYING) return 0;
  int distance = 0;
  while (GameMove(game, 0, 1)) ++distance;
  GameAddScore(game, distance * 2);
  GameLockPiece(game);
  return distance;
}

int GameHold(Game *game) {
  if (game->screen != GAME_PLAYING || game->holdUsed) return 0;
  PieceType current = game->active.type;
  if (game->hasHeld) {
    game->active = SpawnPiece(game->held);
    game->held = current;
    if (!BoardCanPlace(&game->board, game->active)) { game->screen = GAME_OVER; return 0; }
  } else {
    game->held = current;
    game->hasHeld = 1;
    SpawnNext(game);
  }
  game->holdUsed = 1;
  game->gravityTimer = game->lockTimer = 0.0f;
  return 1;
}

float GameGravityInterval(const Game *game) {
  float interval = 0.8f - (float)(game->level - 1) * 0.065f;
  if (interval < 0.05f) interval = 0.05f;
  return interval;
}

void GameUpdate(Game *game, float dt) {
  if (game->screen != GAME_PLAYING || dt <= 0.0f) return;
  if (dt > 0.25f) dt = 0.25f;
  game->gravityTimer += dt;
  float interval = GameGravityInterval(game);
  while (game->gravityTimer >= interval && game->screen == GAME_PLAYING) {
    game->gravityTimer -= interval;
    if (!GameMove(game, 0, 1)) { GameLockPiece(game); break; }
  }
}

void GameTogglePause(Game *game) {
  if (game->screen == GAME_PLAYING) game->screen = GAME_PAUSED;
  else if (game->screen == GAME_PAUSED) game->screen = GAME_PLAYING;
}
