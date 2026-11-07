#include "input.h"
#include <math.h>

static float repeatTimer=0.0f, softTimer=0.0f;
static int repeatingDirection=0;

static int ButtonAt(int mouseX,int mouseY,int centerY) {
  return mouseX>=GetScreenWidth()/2-120 && mouseX<=GetScreenWidth()/2+120 && mouseY>=centerY && mouseY<=centerY+48;
}

void InputHandle(Game *game, Effects *effects, Audio *audio, float dt) {
  if(IsKeyPressed(KEY_M)) AudioToggleMute(audio);
  if(game->screen==GAME_MENU){
    if(IsKeyPressed(KEY_DOWN))game->menuSelection=(game->menuSelection+1)%3;
    if(IsKeyPressed(KEY_UP))game->menuSelection=(game->menuSelection+2)%3;
    if(IsKeyPressed(KEY_C)||IsKeyPressed(KEY_TWO)) game->menuSelection=1;
    if(IsKeyPressed(KEY_Q)) game->menuSelection=2;
    if(IsKeyPressed(KEY_ENTER)||IsKeyPressed(KEY_SPACE)){
      if(game->menuSelection==0){GameStart(game,(unsigned int)GetTime()*100000u+1u);EffectsInit(effects);}
      else if(game->menuSelection==1)game->screen=GAME_CONTROLS;
      else CloseWindow();
    }
    Vector2 mouse=GetMousePosition();
    if(IsMouseButtonPressed(MOUSE_BUTTON_LEFT)){
      if(ButtonAt((int)mouse.x,(int)mouse.y,GetScreenHeight()/2-15)){GameStart(game,(unsigned int)GetTime()*100000u+1u);EffectsInit(effects);}
      else if(ButtonAt((int)mouse.x,(int)mouse.y,GetScreenHeight()/2+48)) game->screen=GAME_CONTROLS;
      else if(ButtonAt((int)mouse.x,(int)mouse.y,GetScreenHeight()/2+111)) CloseWindow();
    }
    return;
  }
  if(game->screen==GAME_CONTROLS){if(IsKeyPressed(KEY_ESCAPE)||IsKeyPressed(KEY_ENTER))game->screen=GAME_MENU;return;}
  if(game->screen==GAME_PAUSED){
    if(IsKeyPressed(KEY_ESCAPE)||IsKeyPressed(KEY_ENTER)||IsKeyPressed(KEY_P))GameTogglePause(game);
    if(IsKeyPressed(KEY_R))GameStart(game,(unsigned int)GetTime()*100000u+1u);
    return;
  }
  if(game->screen==GAME_OVER){
    if(IsKeyPressed(KEY_ENTER)||IsKeyPressed(KEY_R)){GameStart(game,(unsigned int)GetTime()*100000u+1u);EffectsInit(effects);}
    if(IsKeyPressed(KEY_ESCAPE))game->screen=GAME_MENU;
    return;
  }
  if(IsKeyPressed(KEY_ESCAPE)||IsKeyPressed(KEY_P)){GameTogglePause(game);return;}
  if(IsKeyPressed(KEY_X)||IsKeyPressed(KEY_UP)){if(GameRotate(game,1))AudioPlay(audio,SFX_ROTATE);}
  if(IsKeyPressed(KEY_Z)){if(GameRotate(game,-1))AudioPlay(audio,SFX_ROTATE);}
  if(IsKeyPressed(KEY_C)){if(GameHold(game))AudioPlay(audio,SFX_MOVE);}
  if(IsKeyPressed(KEY_SPACE)){if(GameHardDrop(game)>0)AudioPlay(audio,SFX_DROP);}
  int direction=IsKeyDown(KEY_LEFT)?-1:(IsKeyDown(KEY_RIGHT)?1:0);
  if(direction==0){repeatTimer=0;repeatingDirection=0;}
  else if(IsKeyPressed(KEY_LEFT)||IsKeyPressed(KEY_RIGHT)||direction!=repeatingDirection){
    if(GameMove(game,direction,0))AudioPlay(audio,SFX_MOVE);
    repeatingDirection=direction;repeatTimer=0.16f;
  } else {
    repeatTimer-=dt;
    while(repeatTimer<=0){if(GameMove(game,direction,0))AudioPlay(audio,SFX_MOVE);repeatTimer+=0.045f;}
  }
  if(IsKeyDown(KEY_DOWN)){
    softTimer-=dt;
    if(softTimer<=0){if(GameSoftDrop(game))AudioPlay(audio,SFX_SOFT_DROP);softTimer=0.045f;}
  } else softTimer=0;
}
