#include "renderer.h"
#include <math.h>
#include <stdio.h>

static const Color BG = {7, 10, 20, 255};
static const Color DIM = {105, 120, 142, 255};
static const Color PIECE_COLORS[PIECE_COUNT] = {
  {43,220,245,255},{255,206,68,255},{189,93,255,255},{85,239,148,255},
  {255,83,107,255},{80,130,255,255},{255,151,63,255}
};

static void TextCenter(const char *text, int y, int size, Color color) {
  DrawText(text, GetScreenWidth()/2 - MeasureText(text, size)/2, y, size, color);
}

static void DrawPanel(Rectangle r, const char *title) {
  DrawRectangleRounded(r, 0.06f, 8, (Color){13,18,31,245});
  DrawRectangleRoundedLinesEx(r, 0.06f, 8, 1.0f, (Color){40,71,88,255});
  DrawText(title, (int)r.x + 13, (int)r.y + 10, 15, (Color){83,235,178,255});
}

static void DrawCell(int x, int y, float size, Color color, int ghost) {
  Rectangle r = {(float)x + 1, (float)y + 1, size - 2, size - 2};
  if (ghost) {
    color.a = 70;
    DrawRectangleRec(r, color);
    DrawRectangleLinesEx(r, 1.2f, (Color){color.r,color.g,color.b,130});
    return;
  }
  DrawRectangle((int)r.x-2, (int)r.y-2, (int)r.width+4, (int)r.height+4, (Color){color.r,color.g,color.b,22});
  DrawRectangleRounded(r, 0.12f, 3, color);
  DrawRectangle((int)r.x+3, (int)r.y+3, (int)r.width-6, 3, (Color){255,255,255,72});
  DrawRectangleLinesEx(r, 1.0f, (Color){255,255,255,35});
}

static void DrawPiece(Piece p, int originX, int originY, float cell, int ghost) {
  Color color = PIECE_COLORS[p.type];
  for (int y=0; y<4; ++y) for (int x=0; x<4; ++x) {
    if (!PieceCell(p.type,p.rotation,x,y)) continue;
    int bx = p.x+x, by=p.y+y;
    if (by < 0) continue;
    DrawCell(originX+bx*(int)cell, originY+by*(int)cell, cell, color, ghost);
  }
}

static void DrawMini(PieceType type, int x, int y, float cell) {
  int minX=4,minY=4;
  for(int sy=0;sy<4;++sy) for(int sx=0;sx<4;++sx) if(PieceCell(type,0,sx,sy)){if(sx<minX)minX=sx;if(sy<minY)minY=sy;}
  for(int sy=0;sy<4;++sy) for(int sx=0;sx<4;++sx) if(PieceCell(type,0,sx,sy))
    DrawCell(x+(sx-minX)*(int)cell,y+(sy-minY)*(int)cell,cell,PIECE_COLORS[type],0);
}

static void DrawBoard(const Game *g, Effects *fx, int bx, int by, int cell) {
  int width=BOARD_WIDTH*cell, height=BOARD_HEIGHT*cell;
  Rectangle frame={(float)bx-7,(float)by-7,(float)width+14,(float)height+14};
  DrawRectangleRounded(frame,0.025f,8,(Color){11,17,29,255});
  DrawRectangleRoundedLinesEx(frame,0.025f,8,2.0f,(Color){66,233,177,230});
  for(int y=0;y<BOARD_HEIGHT;++y) for(int x=0;x<BOARD_WIDTH;++x){
    Rectangle r={(float)(bx+x*cell),(float)(by+y*cell),(float)cell,(float)cell};
    DrawRectangleLinesEx(r,1,(Color){34,44,59,180});
    int value=g->board.cells[y][x];
    if(value>0) DrawCell(bx+x*cell,by+y*cell,(float)cell,PIECE_COLORS[value-1],0);
  }
  if(g->screen==GAME_PLAYING || g->screen==GAME_PAUSED){
    Piece ghost=g->active;
    while(BoardCanPlace(&g->board,(Piece){ghost.type,ghost.rotation,ghost.x,ghost.y+1})) ++ghost.y;
    if(ghost.y!=g->active.y) DrawPiece(ghost,bx,by,(float)cell,1);
    DrawPiece(g->active,bx,by,(float)cell,0);
  }
  for(int i=0;i<fx->count;++i){
    Particle p=fx->particles[i];
    float alpha=p.life/p.maxLife;
    DrawCircle((int)(bx+(p.position.x+0.5f)*cell),(int)(by+(p.position.y+0.5f)*cell),2.5f,Fade(p.color,alpha));
  }
  if(fx->flash>0) DrawRectangle(bx,by,width,height,Fade(WHITE,fx->flash*0.18f));
  for(int y=0;y<height;y+=4) DrawRectangle(bx,by+y,width,1,(Color){0,0,0,16});
}

static void DrawStats(const Game *g, int x, int y, int width) {
  DrawPanel((Rectangle){(float)x,(float)y,(float)width,135},"SCORE");
  DrawText(TextFormat("%i",g->score),x+14,y+39,24,(Color){241,246,252,255});
  DrawText("BEST",x+14,y+76,13,DIM); DrawText(TextFormat("%i",g->highScore),x+14,y+95,17,(Color){255,205,79,255});
  DrawPanel((Rectangle){(float)x,(float)y+147,(float)width,91},"LEVEL");
  DrawText(TextFormat("%02i",g->level),x+16,y+183,28,(Color){85,235,178,255});
  DrawText(TextFormat("LINES   %03i",g->lines),x+69,y+192,14,DIM);
}

static void DrawGame(const Game *g, Effects *fx, Audio *audio) {
  int w=GetScreenWidth(),h=GetScreenHeight();
  int cell=(int)floorf(fminf((float)h/25.0f,(float)w/36.0f)); if(cell<16)cell=16;
  int bx=(w-BOARD_WIDTH*cell)/2, by=(h-BOARD_HEIGHT*cell)/2;
  int panelW=(w-(BOARD_WIDTH*cell)-76)/2; if(panelW<120)panelW=120; if(panelW>195)panelW=195;
  int lx=bx-panelW-22, rx=bx+BOARD_WIDTH*cell+22, py=by+8;
  DrawText("HOLD",lx,py,15,(Color){83,235,178,255});
  DrawPanel((Rectangle){(float)lx,(float)py+24,(float)panelW,105},"");
  if(g->hasHeld) DrawMini(g->held,lx+panelW/2-28,py+57,22);
  DrawText("C   hold",lx,py+150,13,DIM);
  DrawText("SPACE  hard drop",lx,py+171,13,DIM);
  DrawText("P / ESC  pause",lx,py+192,13,DIM);
  DrawBoard(g,fx,bx,by,cell);
  DrawText("NEXT",rx,py,15,(Color){83,235,178,255});
  DrawPanel((Rectangle){(float)rx,(float)py+24,(float)panelW,200},"");
  for(int i=0;i<NEXT_QUEUE_SIZE;++i) DrawMini(g->queue[i],rx+panelW/2-28,py+46+i*34,17);
  DrawStats(g,rx,py+240,panelW);
  DrawText(audio->muted?"AUDIO OFF [M]":"AUDIO ON [M]",rx,py+492,12,DIM);
}

static void DrawButton(const char *label, int y, int selected) {
  int w=240,h=48,x=GetScreenWidth()/2-w/2;
  Color c=selected?(Color){49,222,160,255}:(Color){31,51,66,255};
  DrawRectangleRounded((Rectangle){(float)x,(float)y,(float)w,(float)h},0.18f,8,c);
  DrawRectangleRoundedLinesEx((Rectangle){(float)x,(float)y,(float)w,(float)h},0.18f,8,1.5f,(Color){91,247,192,220});
  int size=20; DrawText(label,x+w/2-MeasureText(label,size)/2,y+13,size,selected?BG:(Color){221,233,239,255});
}

static void DrawMenu(const Game *g) {
  int w=GetScreenWidth(),h=GetScreenHeight();
  for(int i=0;i<20;++i){int y=(i*97+(int)(GetTime()*22))%h; DrawLine(0,y,w,y,(Color){18,36,45,110});}
  DrawText("TETRIS",w/2-160,h/5,76,(Color){86,241,178,255});
  DrawText("N E O N   A R C A D E",w/2-105,h/5+82,17,(Color){104,150,162,255});
  Vector2 mouse=GetMousePosition();
  int hover=-1;
  for(int i=0;i<3;++i)if(CheckCollisionPointRec(mouse,(Rectangle){(float)(w/2-120),(float)(h/2-15+i*63),240,48}))hover=i;
  DrawButton("PLAY",h/2-15,hover==0|| (hover<0&&g->menuSelection==0));
  DrawButton("CONTROLS",h/2+48,hover==1|| (hover<0&&g->menuSelection==1));
  DrawButton("QUIT",h/2+111,hover==2|| (hover<0&&g->menuSelection==2));
  TextCenter("ARROWS  MOVE     Z / X  ROTATE     SPACE  DROP",h-68,14,DIM);
  (void)g;
}

static void DrawControls(void) {
  TextCenter("CONTROLS",120,48,(Color){86,241,178,255});
  const char *lines[]={"LEFT / RIGHT       Move piece","DOWN               Soft drop","SPACE              Hard drop","Z                  Rotate counterclockwise","X / UP              Rotate clockwise","C                  Hold piece","P / ESC            Pause","M                  Toggle sound"};
  for(int i=0;i<8;++i) TextCenter(lines[i],220+i*42,22,(Color){218,228,239,255});
  TextCenter("ENTER / ESC  BACK",590,17,DIM);
}

static void DrawOverlay(const Game *g, int gameOver) {
  int w=GetScreenWidth(),h=GetScreenHeight();
  DrawRectangle(0,0,w,h,(Color){3,6,12,205});
  TextCenter(gameOver?"GAME OVER":"PAUSED",h/3,52,gameOver?(Color){255,104,119,255}:(Color){88,241,178,255});
  if(gameOver){TextCenter(TextFormat("SCORE  %i",g->score),h/3+74,23,WHITE);TextCenter(TextFormat("BEST   %i",g->highScore),h/3+112,19,(Color){255,205,79,255});}
  TextCenter(gameOver?"ENTER  RESTART       ESC  MENU":"ENTER  RESUME       R  RESTART",h/2+45,18,WHITE);
}

void RenderGame(const Game *game, Effects *effects, Audio *audio) {
  BeginDrawing();
  ClearBackground(BG);
  for(int i=0;i<42;++i){int x=(i*157+(int)(GetTime()*9))%GetScreenWidth();int y=(i*83+(i%5)*11)%GetScreenHeight();DrawPixel(x,y,(Color){30,76,84,115});}
  if(game->screen==GAME_MENU) DrawMenu(game);
  else if(game->screen==GAME_CONTROLS) DrawControls();
  else {
    DrawGame(game,effects,audio);
    if(game->screen==GAME_PAUSED) DrawOverlay(game,0);
    else if(game->screen==GAME_OVER) DrawOverlay(game,1);
  }
  EndDrawing();
}
