#ifndef TETRIS_TETROMINO_H
#define TETRIS_TETROMINO_H
typedef enum { PIECE_I, PIECE_O, PIECE_T, PIECE_S, PIECE_Z, PIECE_J, PIECE_L, PIECE_COUNT } PieceType;
#define PIECE_MATRIX 4
typedef struct { PieceType type; int rotation; int x; int y; } Piece;
extern const unsigned char PIECE_SHAPES[PIECE_COUNT][PIECE_MATRIX][PIECE_MATRIX];
int PieceCell(PieceType type, int rotation, int x, int y);
const char *PieceName(PieceType type);
#endif
