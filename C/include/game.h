#ifndef TETRIS_GAME_H
#define TETRIS_GAME_H
#include "board.h"
#define NEXT_QUEUE_SIZE 5
typedef enum { GAME_MENU, GAME_CONTROLS, GAME_PLAYING, GAME_PAUSED, GAME_OVER } GameScreen;
typedef struct {
  Board board;
  Piece active;
  PieceType queue[NEXT_QUEUE_SIZE];
  PieceType bag[PIECE_COUNT];
  int bagIndex;
  PieceType held;
  int hasHeld;
  int holdUsed;
  int score;
  int highScore;
  int lines;
  int level;
  int menuSelection;
  int lockCount;
  float gravityTimer;
  float lockTimer;
  GameScreen screen;
  unsigned int rng;
} Game;
void GameInit(Game *game, unsigned int seed, int highScore);
void GameStart(Game *game, unsigned int seed);
int GameMove(Game *game, int dx, int dy);
int GameSoftDrop(Game *game);
int GameRotate(Game *game, int direction);
int GameHardDrop(Game *game);
int GameHold(Game *game);
void GameUpdate(Game *game, float dt);
float GameGravityInterval(const Game *game);
int GameLockPiece(Game *game);
void GameTogglePause(Game *game);
void GameAddScore(Game *game, int points);
#endif
