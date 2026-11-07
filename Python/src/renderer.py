"""Responsive warm-neutral Pygame renderer."""
from __future__ import annotations
import math
from dataclasses import dataclass
import pygame
from .config import ACCENT,BG_BOTTOM,BG_TOP,BOARD_SURFACE,COLORS,GRID,HEIGHT,INK,MUTED,SURFACE,WIDTH
from .effects import Effects
from .game import Game,Screen
from .tetromino import Piece,local_cells

@dataclass(frozen=True)
class Layout:
    width:int;height:int;cell:int;bx:int;by:int;panel:int;left:int;right:int

class Renderer:
    def __init__(self,surface):
        self.surface=surface;self.fonts={};self.buttons={};self.last_screen=None;self.fade=.25;self.score=object();self.score_pulse=0.;self.menu_selection=0
    def resize(self,surface):self.surface=surface
    def layout(self):
        w,h=self.surface.get_size();cell=max(18,min(34,(h-160)//HEIGHT,(w-400)//WIDTH));bx=(w-WIDTH*cell)//2;by=(h-HEIGHT*cell)//2+14
        panel=min(194,max(150,(w-WIDTH*cell-96)//2));return Layout(w,h,cell,bx,by,panel,bx-panel-26,bx+WIDTH*cell+26)
    def font(self,size,bold=False):
        key=(size,bold)
        if key not in self.fonts:self.fonts[key]=pygame.font.SysFont("segoeui,aptos,arial",size,bold=bold)
        return self.fonts[key]
    def text(self,s,x,y,size,color=INK,bold=False,center=False):
        img=self.font(size,bold).render(str(s),True,color);r=img.get_rect()
        if center:r.midtop=(x,y)
        else:r.topleft=(x,y)
        self.surface.blit(img,r);return r
    def panel(self,r,radius=13,color=SURFACE):
        shadow=pygame.Surface((r.width+8,r.height+10),pygame.SRCALPHA);pygame.draw.rect(shadow,(37,49,54,22),shadow.get_rect().inflate(-8,-10),border_radius=radius+2);self.surface.blit(shadow,(r.x,r.y+4))
        pygame.draw.rect(self.surface,color,r,border_radius=radius);pygame.draw.rect(self.surface,(232,234,230),r,1,border_radius=radius)
    def buttons_for(self,g):
        w,h=self.surface.get_size();cx=w//2
        if g.state==Screen.MENU:
            y=h//2-8;return {"play":pygame.Rect(cx-124,y,248,52),"controls":pygame.Rect(cx-124,y+68,248,52),"quit":pygame.Rect(cx-124,y+136,248,52)}
        if g.state==Screen.CONTROLS:return {"back":pygame.Rect(cx-124,h-100,248,52)}
        if g.state==Screen.PAUSED:
            y=h//2-4;return {"resume":pygame.Rect(cx-124,y,248,50),"restart":pygame.Rect(cx-124,y+64,248,50),"menu":pygame.Rect(cx-124,y+128,248,50)}
        if g.state==Screen.GAME_OVER:
            y=h//2+52;return {"restart":pygame.Rect(cx-124,y,248,50),"menu":pygame.Rect(cx-124,y+64,248,50)}
        return {}
    def button(self,key,label,rect,selected=False):
        hover=selected or rect.collidepoint(pygame.mouse.get_pos());fill=ACCENT if hover else SURFACE;fg=(255,255,255) if hover else INK
        pygame.draw.rect(self.surface,(37,49,54,20),rect.move(0,4),border_radius=12);pygame.draw.rect(self.surface,fill,rect,border_radius=12);pygame.draw.rect(self.surface,ACCENT if hover else (222,225,220),rect,1,border_radius=12)
        self.text(label,rect.centerx,rect.y+15,16,fg,True,True);self.buttons[key]=rect
    def background(self,t):
        w,h=self.surface.get_size()
        for y in range(h):
            k=y/max(1,h-1);c=tuple(round(a+(b-a)*k) for a,b in zip(BG_TOP,BG_BOTTOM));pygame.draw.line(self.surface,c,(0,y),(w,y))
        d=int(math.sin(t*.25)*15);pygame.draw.circle(self.surface,(244,243,237),(-90+d,h//3),215);pygame.draw.circle(self.surface,(242,244,239),(w+80-d,h*2//3),175)
    def draw(self,g,effects,t,muted):
        if self.last_screen!=g.state:self.last_screen=g.state;self.fade=0.
        self.fade=min(.25,self.fade+1/60)
        if self.score!=g.score:self.score_pulse=.28 if self.score is not object else 0.;self.score=g.score
        self.score_pulse=max(0,self.score_pulse-1/60);self.background(t)
        if g.state==Screen.MENU:self.draw_menu(g,t)
        elif g.state==Screen.CONTROLS:self.draw_controls(g)
        else:
            self.draw_game(g,effects,muted)
            if g.state in (Screen.PAUSED,Screen.GAME_OVER):self.draw_overlay(g)
        if self.fade<.25:
            veil=pygame.Surface(self.surface.get_size(),pygame.SRCALPHA);veil.fill((248,247,243,int((.25-self.fade)*70)));self.surface.blit(veil,(0,0))
    def draw_menu(self,g,t):
        w,h=self.surface.get_size();cx=w//2;pygame.draw.circle(self.surface,(234,239,234),(int(w*.17),int(h*.3+math.sin(t)*8)),50,1);pygame.draw.circle(self.surface,(234,239,234),(int(w*.82),int(h*.68+math.cos(t)*8)),68,1)
        self.text("T E T R I S",cx,h//4,48,INK,True,True);self.text("A QUIET GAME OF SPATIAL RHYTHM",cx,h//4+62,13,MUTED,False,True)
        self.buttons=self.buttons_for(g)
        for i,(key,label) in enumerate((("play","PLAY"),("controls","CONTROLS"),("quit","QUIT"))):self.button(key,label,self.buttons[key],self.menu_selection==i)
        self.text("←  →  MOVE     ↓  SOFT DROP     SPACE  DROP",cx,h-57,12,MUTED,False,True)
    def draw_controls(self,g):
        w,h=self.surface.get_size();cx=w//2;self.text("CONTROLS",cx,55,34,INK,True,True)
        rows=(("← / A","Move left"),("→ / D","Move right"),("↓ / S","Soft drop"),("↑ / X","Rotate clockwise"),("Z","Rotate counterclockwise"),("SPACE","Hard drop"),("C / SHIFT","Hold piece"),("P / ESC","Pause"),("R","Restart"),("M","Toggle sound"))
        y=max(145,h//2-180)
        for i,(key,action) in enumerate(rows):self.text(key,cx-180,y+i*34,15,ACCENT,True);self.text(action,cx-8,y+i*34,15,INK)
        self.buttons=self.buttons_for(g);self.button("back","BACK",self.buttons["back"])
    def block(self,r,color,ghost=False):
        inset=max(1,r.width//12);r=r.inflate(-2*inset,-2*inset)
        if ghost:
            s=pygame.Surface(r.size,pygame.SRCALPHA);pygame.draw.rect(s,(*color,45),s.get_rect(),border_radius=5);pygame.draw.rect(s,(*color,145),s.get_rect(),1,border_radius=5);self.surface.blit(s,r);return
        pygame.draw.rect(self.surface,tuple(max(0,c-25) for c in color),r.move(0,2),border_radius=5);pygame.draw.rect(self.surface,color,r,border_radius=5)
        if r.height>=14:pygame.draw.line(self.surface,tuple(min(255,c+28) for c in color),(r.x+5,r.y+3),(r.right-5,r.y+3),1)
    def draw_piece(self,p,bx,by,cell,ghost=False):
        for x,y in local_cells(p.kind,p.rotation):
            gx,gy=p.x+x,p.y+y
            if gy>=0:self.block(pygame.Rect(bx+gx*cell,by+gy*cell,cell,cell),COLORS[p.kind],ghost)
    def preview(self,kind,bounds):
        cells=local_cells(kind);minx=min(x for x,y in cells);maxx=max(x for x,y in cells);miny=min(y for x,y in cells);maxy=max(y for x,y in cells)
        size=max(10,min(17,(bounds.width-22)//(maxx-minx+1),(bounds.height-8)//(maxy-miny+1)));ox=bounds.centerx-(maxx-minx+1)*size//2;oy=bounds.centery-(maxy-miny+1)*size//2
        for x,y in cells:self.block(pygame.Rect(ox+(x-minx)*size,oy+(y-miny)*size,size,size),COLORS[kind])
    def draw_game(self,g,effects,muted):
        l=self.layout();cell,bx,by=l.cell,l.bx,l.by;self.text("TETRIS",l.width//2,17,17,INK,True,True);self.text("MINIMAL EDITION",l.width//2,41,10,MUTED,False,True)
        self.panel(pygame.Rect(bx-8,by-8,WIDTH*cell+16,HEIGHT*cell+16));pygame.draw.rect(self.surface,BOARD_SURFACE,(bx,by,WIDTH*cell,HEIGHT*cell),border_radius=5)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                r=pygame.Rect(bx+x*cell,by+y*cell,cell,cell);pygame.draw.rect(self.surface,GRID,r,1);kind=g.board.grid[y][x]
                if kind:self.block(r,COLORS[kind])
        if g.state in (Screen.PLAYING,Screen.PAUSED):self.draw_piece(g.ghost_piece(),bx,by,cell,True);self.draw_piece(g.active,bx,by,cell)
        for p in effects.particles:
            alpha=max(0,min(255,int(255*p.life/p.duration)));r=max(1,int(2+2*alpha/255));s=pygame.Surface((r*2,r*2),pygame.SRCALPHA);pygame.draw.circle(s,(*p.color,alpha),(r,r),r);self.surface.blit(s,(bx+int(p.x*cell)-r,by+int(p.y*cell)-r))
        self.side(g,l,muted)
    def side(self,g,l,muted):
        x,y,w=l.left,l.by+2,l.panel;right=l.right
        self.text("HOLD",x,y,12,MUTED,True);r=pygame.Rect(x,y+23,w,106);self.panel(r)
        if g.held:self.preview(g.held,r)
        for i,s in enumerate(("C / SHIFT  ·  Hold once per piece","P / ESC  ·  Pause","R  ·  Restart")):self.text(s,x,y+148+i*24,11,MUTED)
        self.text("NEXT",right,y,12,MUTED,True);r=pygame.Rect(right,y+23,w,268);self.panel(r)
        for i,k in enumerate(g.next_queue):self.preview(k,pygame.Rect(right+8,y+28+i*46,w-16,46))
        stats=pygame.Rect(right,y+284,w,200);self.panel(stats);self.text("SCORE",right+16,stats.y+15,10,MUTED,True);self.text(f"{g.score:,}",right+16,stats.y+32,29,INK,True)
        self.text("BEST",right+16,stats.y+77,10,MUTED,True);self.text(f"{g.high_score:,}",right+16,stats.y+94,16,ACCENT,True);pygame.draw.line(self.surface,GRID,(right+16,stats.y+127),(right+w-16,stats.y+127))
        self.text("LEVEL",right+16,stats.y+140,9,MUTED,True);self.text(g.level,right+16,stats.y+156,18,INK,True);self.text("LINES",right+w//2+4,stats.y+140,9,MUTED,True);self.text(g.lines,right+w//2+4,stats.y+156,18,INK,True);self.text("SOUND · "+("OFF" if muted else "ON")+" [M]",right,stats.bottom+10,10,MUTED)
    def draw_overlay(self,g):
        w,h=self.surface.get_size();veil=pygame.Surface((w,h),pygame.SRCALPHA);veil.fill((38,44,46,150));self.surface.blit(veil,(0,0));r=pygame.Rect(w//2-188,h//2-168,376,410 if g.state==Screen.GAME_OVER else 350);self.panel(r,18)
        if g.state==Screen.PAUSED:self.text("PAUSED",w//2,r.y+43,32,INK,True,True);self.text("Take your time.",w//2,r.y+91,14,MUTED,False,True);labels=(("resume","RESUME"),("restart","RESTART"),("menu","MAIN MENU"))
        else:self.text("GAME OVER",w//2,r.y+35,29,INK,True,True);self.text("FINAL SCORE",w//2,r.y+115,10,MUTED,True,True);self.text(f"{g.score:,}",w//2,r.y+135,30,INK,True,True);self.text(f"BEST  {g.high_score:,}",w//2,r.y+179,12,ACCENT,True,True);labels=(("restart","RESTART"),("menu","MAIN MENU"))
        self.buttons=self.buttons_for(g)
        for k,label in labels:self.button(k,label,self.buttons[k])
