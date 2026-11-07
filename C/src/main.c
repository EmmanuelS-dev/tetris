#include "renderer.h"
#include "input.h"
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#if defined(_WIN32)
#include <direct.h>
#else
#include <sys/stat.h>
#endif

static void HighScorePath(char *path,size_t size) {
#if defined(_WIN32)
  const char *root=getenv("APPDATA");
  if(root&&*root){snprintf(path,size,"%s/C-Tetris",root);_mkdir(path);snprintf(path,size,"%s/C-Tetris/highscore.txt",root);return;}
#else
  const char *root=getenv("XDG_DATA_HOME");
  if(!root||!*root){const char *home=getenv("HOME");if(home&&*home){static char fallback[1024];snprintf(fallback,sizeof(fallback),"%s/.local/share",home);root=fallback;}}
  if(root&&*root){snprintf(path,size,"%s/C-Tetris",root);mkdir(path,0755);snprintf(path,size,"%s/C-Tetris/highscore.txt",root);return;}
#endif
  snprintf(path,size,"highscore.txt");
}
static int ReadHighScore(const char *path){FILE *f=fopen(path,"r");int score=0;if(f){(void)fscanf(f,"%d",&score);fclose(f);}return score>0?score:0;}
static void WriteHighScore(const char *path,int score){FILE *f=fopen(path,"w");if(f){fprintf(f,"%d\n",score);fclose(f);}}

int main(void) {
  SetConfigFlags(FLAG_WINDOW_RESIZABLE|FLAG_VSYNC_HINT|FLAG_MSAA_4X_HINT);
  InitWindow(1000,760,"TETRIS // NEON ARCADE");
  SetExitKey(KEY_NULL);
  SetWindowMinSize(800,600);
  SetTargetFPS(60);
  char scorePath[1200];HighScorePath(scorePath,sizeof(scorePath));
  Game game;GameInit(&game,(unsigned int)time(NULL),ReadHighScore(scorePath));
  Effects effects;EffectsInit(&effects);
  Audio audio;AudioInit(&audio);
  int previousHigh=game.highScore;
  while(!WindowShouldClose()){
    float dt=GetFrameTime();
    int previousLines=game.lines, previousLevel=game.level;
    int previousLocks=game.lockCount;
    GameScreen previousScreen=game.screen;
    InputHandle(&game,&effects,&audio,dt);
    GameUpdate(&game,dt);
    if(game.lockCount>previousLocks)AudioPlay(&audio,SFX_LOCK);
    if(game.lines>previousLines){int cleared=game.lines-previousLines;EffectsClear(&effects,&game.board,cleared);AudioPlay(&audio,cleared==4?SFX_TETRIS:SFX_CLEAR);}
    if(game.level>previousLevel)AudioPlay(&audio,SFX_LEVEL);
    if(game.screen==GAME_OVER&&previousScreen!=GAME_OVER)AudioPlay(&audio,SFX_GAMEOVER);
    EffectsUpdate(&effects,dt);
    if(game.highScore!=previousHigh){WriteHighScore(scorePath,game.highScore);previousHigh=game.highScore;}
    RenderGame(&game,&effects,&audio);
  }
  WriteHighScore(scorePath,game.highScore);
  AudioClose(&audio);CloseWindow();
  return 0;
}
