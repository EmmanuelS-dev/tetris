#include "board.h"
#include <string.h>

void BoardClear(Board *board) { memset(board, 0, sizeof(*board)); }

int BoardCanPlace(const Board *board, Piece piece) {
  for (int y = 0; y < 4; ++y) for (int x = 0; x < 4; ++x) {
    if (!PieceCell(piece.type, piece.rotation, x, y)) continue;
    int bx = piece.x + x, by = piece.y + y;
    if (bx < 0 || bx >= BOARD_WIDTH || by >= BOARD_HEIGHT) return 0;
    if (by >= 0 && board->cells[by][bx] != 0) return 0;
  }
  return 1;
}

int BoardLock(Board *board, Piece piece) {
  int toppedOut = 0;
  if (!BoardCanPlace(board, piece)) return -1;
  for (int y = 0; y < 4; ++y) for (int x = 0; x < 4; ++x) {
    if (!PieceCell(piece.type, piece.rotation, x, y)) continue;
    int bx = piece.x + x, by = piece.y + y;
    if (by < 0) toppedOut = 1;
    else board->cells[by][bx] = (int)piece.type + 1;
  }
  return toppedOut;
}

int BoardClearLines(Board *board) {
  int write = BOARD_HEIGHT - 1, cleared = 0;
  for (int read = BOARD_HEIGHT - 1; read >= 0; --read) {
    int full = 1;
    for (int x = 0; x < BOARD_WIDTH; ++x) if (board->cells[read][x] == 0) { full = 0; break; }
    if (full) { ++cleared; continue; }
    if (write != read) memcpy(board->cells[write], board->cells[read], sizeof(board->cells[read]));
    --write;
  }
  while (write >= 0) memset(board->cells[write--], 0, sizeof(board->cells[0]));
  return cleared;
}

int BoardIsTopOut(const Board *board) {
  for (int x = 0; x < BOARD_WIDTH; ++x) if (board->cells[0][x]) return 1;
  return 0;
}
