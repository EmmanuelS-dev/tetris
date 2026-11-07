#ifndef TETRIS_BOARD_H
#define TETRIS_BOARD_H
#include "tetromino.h"
#define BOARD_WIDTH 10
#define BOARD_HEIGHT 20
typedef struct { int cells[BOARD_HEIGHT][BOARD_WIDTH]; } Board;
void BoardClear(Board *board);
int BoardCanPlace(const Board *board, Piece piece);
int BoardLock(Board *board, Piece piece);
int BoardClearLines(Board *board);
int BoardIsTopOut(const Board *board);
#endif
