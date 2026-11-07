#include "tetromino.h"

const unsigned char PIECE_SHAPES[PIECE_COUNT][4][4] = {
  {{0,0,0,0},{1,1,1,1},{0,0,0,0},{0,0,0,0}},
  {{0,1,1,0},{0,1,1,0},{0,0,0,0},{0,0,0,0}},
  {{0,1,0,0},{1,1,1,0},{0,0,0,0},{0,0,0,0}},
  {{0,1,1,0},{1,1,0,0},{0,0,0,0},{0,0,0,0}},
  {{1,1,0,0},{0,1,1,0},{0,0,0,0},{0,0,0,0}},
  {{1,0,0,0},{1,1,1,0},{0,0,0,0},{0,0,0,0}},
  {{0,0,1,0},{1,1,1,0},{0,0,0,0},{0,0,0,0}}
};

int PieceCell(PieceType type, int rotation, int x, int y) {
  if ((unsigned)type >= PIECE_COUNT || x < 0 || y < 0 || x >= 4 || y >= 4) return 0;
  rotation = (rotation % 4 + 4) % 4;
  int sx = x, sy = y;
  for (int i = 0; i < rotation; ++i) { int nextX = sy; sy = 3 - sx; sx = nextX; }
  return PIECE_SHAPES[type][sy][sx] != 0;
}

const char *PieceName(PieceType type) {
  static const char *names[] = {"I", "O", "T", "S", "Z", "J", "L"};
  return (unsigned)type < PIECE_COUNT ? names[type] : "?";
}
