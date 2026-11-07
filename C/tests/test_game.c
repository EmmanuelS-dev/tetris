#include "game.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>

static void TestShapes(void) {
  for (int type=0;type<PIECE_COUNT;++type) {
    int count=0;
    for(int y=0;y<4;++y)for(int x=0;x<4;++x)count+=PieceCell((PieceType)type,0,x,y);
    assert(count==4);
  }
  assert(strcmp(PieceName(PIECE_T),"T")==0);
}

static void TestMovementAndCollision(void) {
  Game g;GameStart(&g,1234);
  g.active=(Piece){PIECE_O,0,3,5};
  assert(GameMove(&g,-1,0));
  assert(GameMove(&g,1,0));
  g.active.x=-2;assert(!BoardCanPlace(&g.board,g.active));
  g.active=(Piece){PIECE_O,0,3,18};assert(BoardCanPlace(&g.board,g.active));
  assert(!GameMove(&g,0,1));
  g.board.cells[19][4]=PIECE_T+1;assert(!BoardCanPlace(&g.board,g.active));
}

static void TestRotationAndWallKick(void) {
  Game g;GameStart(&g,7);
  g.active=(Piece){PIECE_T,0,3,5};
  assert(GameRotate(&g,1));assert(g.active.rotation==1);
  assert(GameRotate(&g,-1));assert(g.active.rotation==0);
  g.active=(Piece){PIECE_I,1,-1,5};
  assert(BoardCanPlace(&g.board,g.active));
  assert(GameRotate(&g,-1));
  assert(g.active.rotation==0&&g.active.x==1);
  g.active=(Piece){PIECE_O,0,3,5};
  assert(GameRotate(&g,1));assert(g.active.rotation==0);
}

static void TestLockAndLineClears(void) {
  const int expectedScores[]={0,100,300,500,800};
  for(int lines=1;lines<=4;++lines){
    Game g;GameStart(&g,11);
    for(int y=BOARD_HEIGHT-lines;y<BOARD_HEIGHT;++y)
      for(int x=0;x<BOARD_WIDTH;++x)if(y<BOARD_HEIGHT-2||x<5||x>6)g.board.cells[y][x]=PIECE_J+1;
    g.active=(Piece){PIECE_O,0,4,BOARD_HEIGHT-2};
    assert(GameLockPiece(&g)==lines);
    assert(g.score==expectedScores[lines]);
    assert(g.lines==lines);
    for(int y=0;y<lines;++y)for(int x=0;x<BOARD_WIDTH;++x)assert(g.board.cells[y][x]==0);
  }
  Game g;GameStart(&g,2);g.active=(Piece){PIECE_T,0,3,-2};
  assert(GameLockPiece(&g)==0);
  assert(g.screen==GAME_OVER);
}

static void TestScoringAndLevel(void) {
  Game g;GameStart(&g,1);
  GameAddScore(&g,100);assert(g.score==100&&g.highScore==100);
  g.lines=9;g.level=1;
  for(int y=BOARD_HEIGHT-2;y<BOARD_HEIGHT;++y)
    for(int x=0;x<BOARD_WIDTH;++x)if(x<5||x>6)g.board.cells[y][x]=1;
  g.active=(Piece){PIECE_O,0,4,BOARD_HEIGHT-2};
  assert(GameLockPiece(&g)==2);
  assert(g.level==2&&g.lines==11);
  assert(g.score==100+300);
  assert(GameGravityInterval(&g)<0.8f);
  g.level=99;assert(GameGravityInterval(&g)>=0.05f);
}

static void TestDropScoring(void) {
  Game g;GameStart(&g,10);g.active=(Piece){PIECE_O,0,3,5};
  assert(GameSoftDrop(&g));assert(g.score==1&&g.active.y==6);
  int distance=GameHardDrop(&g);
  assert(distance==12);
  assert(g.score==25);
  assert(g.lockCount==1);
}

static void TestSevenBagAndQueue(void) {
  Game g;GameStart(&g,0x12345678u);
  int seen[PIECE_COUNT]={0};
  for(int i=0;i<PIECE_COUNT;++i)++seen[g.bag[i]];
  for(int i=0;i<PIECE_COUNT;++i)assert(seen[i]==1);
  for(int i=0;i<NEXT_QUEUE_SIZE;++i)assert((unsigned)g.queue[i]<PIECE_COUNT);
}

static void TestHoldAndPause(void) {
  Game g;GameStart(&g,5);
  PieceType first=g.active.type;
  assert(GameHold(&g));assert(g.hasHeld&&g.held==first&&g.holdUsed);
  assert(!GameHold(&g));
  assert(GameHardDrop(&g)>=0);
  assert(!g.holdUsed||g.screen==GAME_OVER);
  if(g.screen==GAME_PLAYING){PieceType dropped=g.active.type;assert(GameHold(&g));assert(g.active.type==first);assert(g.held==dropped);}
  GameTogglePause(&g);assert(g.screen==GAME_PAUSED);
  GameUpdate(&g,10.0f);GameTogglePause(&g);assert(g.screen==GAME_PLAYING||g.screen==GAME_OVER);
}

int main(void) {
  TestShapes();TestMovementAndCollision();TestRotationAndWallKick();TestLockAndLineClears();
  TestScoringAndLevel();TestDropScoring();TestSevenBagAndQueue();TestHoldAndPause();
  puts("All gameplay tests passed.");
  return 0;
}
