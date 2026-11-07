"""Pygame events, DAS/ARR, and controls."""
import pygame
from .audio import Audio
from .effects import Effects
from .game import Game,Screen
from .renderer import Renderer

DAS,ARR=.16,.045
class InputHandler:
    def __init__(self,renderer:Renderer,audio:Audio,effects:Effects):
        self.renderer=renderer;self.audio=audio;self.effects=effects;self.down=set();self.delay=0.;self.soft=0.;self.direction=0;self.running=True
    def active_direction(self):
        left=any(k in self.down for k in (pygame.K_LEFT,pygame.K_a));right=any(k in self.down for k in (pygame.K_RIGHT,pygame.K_d))
        return self.direction if left and right else (-1 if left else 1 if right else 0)
    def start(self,g):g.start_game();self.down.clear();self.delay=self.soft=0.
    def process(self,events,g):
        for e in events:
            if e.type==pygame.QUIT:self.running=False
            elif e.type==pygame.WINDOWFOCUSLOST:self.down.clear();self.delay=self.soft=0.
            elif e.type==pygame.MOUSEBUTTONDOWN and e.button==1:self.click(e.pos,g)
            elif e.type==pygame.KEYUP:self.keyup(e.key)
            elif e.type==pygame.KEYDOWN:self.keydown(e.key,g)
        return self.running
    def click(self,pos,g):
        buttons=self.renderer.buttons_for(g);choice=next((k for k,r in buttons.items() if r.collidepoint(pos)),None)
        if g.state==Screen.MENU:
            if choice=="play":self.start(g)
            elif choice=="controls":g.state=Screen.CONTROLS
            elif choice=="quit":self.running=False
        elif g.state==Screen.CONTROLS and choice=="back":g.state=Screen.MENU
        elif g.state==Screen.PAUSED:
            if choice=="resume":g.toggle_pause()
            elif choice=="restart":self.start(g)
            elif choice=="menu":g.state=Screen.MENU
        elif g.state==Screen.GAME_OVER:
            if choice=="restart":self.start(g)
            elif choice=="menu":g.state=Screen.MENU
    def keydown(self,k,g):
        if k==pygame.K_m:self.audio.toggle();return
        if g.state==Screen.MENU:
            if k in (pygame.K_DOWN,pygame.K_s):self.renderer.menu_selection=(self.renderer.menu_selection+1)%3
            elif k in (pygame.K_UP,pygame.K_w):self.renderer.menu_selection=(self.renderer.menu_selection-1)%3
            elif k in (pygame.K_RETURN,pygame.K_SPACE):
                selection=("play","controls","quit")[self.renderer.menu_selection]
                if selection=="play":self.start(g)
                elif selection=="controls":g.state=Screen.CONTROLS
                else:self.running=False
            elif k==pygame.K_c:g.state=Screen.CONTROLS
            elif k==pygame.K_q:self.running=False
            return
        if g.state==Screen.CONTROLS:
            if k in (pygame.K_ESCAPE,pygame.K_RETURN):g.state=Screen.MENU
            return
        if g.state==Screen.PAUSED:
            if k in (pygame.K_ESCAPE,pygame.K_p,pygame.K_RETURN):g.toggle_pause()
            elif k==pygame.K_r:self.start(g)
            return
        if g.state==Screen.GAME_OVER:
            if k in (pygame.K_r,pygame.K_RETURN):self.start(g)
            elif k==pygame.K_ESCAPE:g.state=Screen.MENU
            return
        if g.state!=Screen.PLAYING:return
        if k in (pygame.K_p,pygame.K_ESCAPE):g.toggle_pause();self.down.clear();return
        if k==pygame.K_r:self.start(g);return
        if k in (pygame.K_UP,pygame.K_x):g.rotate(1);return
        if k==pygame.K_z:g.rotate(-1);return
        if k in (pygame.K_c,pygame.K_LSHIFT,pygame.K_RSHIFT):g.hold_piece();return
        if k==pygame.K_SPACE:g.hard_drop();return
        direction=-1 if k in (pygame.K_LEFT,pygame.K_a) else 1 if k in (pygame.K_RIGHT,pygame.K_d) else 0
        if direction:
            if k not in self.down:self.down.add(k);self.direction=direction;g.move(direction,0);self.delay=DAS
            return
        if k in (pygame.K_DOWN,pygame.K_s) and k not in self.down:self.down.add(k);g.soft_drop();self.soft=ARR
    def keyup(self,k):
        self.down.discard(k)
        if k in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_a,pygame.K_d):
            self.direction=self.active_direction();self.delay=DAS if self.direction else 0.
        if k in (pygame.K_DOWN,pygame.K_s) and not any(x in self.down for x in (pygame.K_DOWN,pygame.K_s)):self.soft=0.
    def update(self,dt,g):
        if g.state!=Screen.PLAYING:return
        d=self.active_direction()
        if d:
            self.delay-=dt
            while self.delay<=0:g.move(d,0);self.delay+=ARR
        if any(k in self.down for k in (pygame.K_DOWN,pygame.K_s)):
            self.soft-=dt
            while self.soft<=0:g.soft_drop();self.soft+=ARR
