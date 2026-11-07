"""Graphics-independent game rules, shared with the C implementation."""
from enum import Enum
from .board import Board
from .config import QUEUE_SIZE
from .piece_generator import PieceGenerator
from .tetromino import Piece

LINE_POINTS=(0,100,300,500,800)
class Screen(str,Enum): MENU="menu"; CONTROLS="controls"; PLAYING="playing"; PAUSED="paused"; GAME_OVER="game_over"

JLSTZ=(
 ((0,0),(-1,0),(-1,-1),(0,2),(-1,2)), ((0,0),(1,0),(1,1),(0,-2),(1,-2)),
 ((0,0),(1,0),(1,1),(0,-2),(1,-2)), ((0,0),(-1,0),(-1,-1),(0,2),(-1,2)),
 ((0,0),(1,0),(1,-1),(0,2),(1,2)), ((0,0),(-1,0),(-1,1),(0,-2),(-1,-2)),
 ((0,0),(-1,0),(-1,1),(0,-2),(-1,-2)), ((0,0),(1,0),(1,-1),(0,2),(1,2)))
I_KICKS=(
 ((0,0),(-2,0),(1,0),(-2,-1),(1,2)), ((0,0),(-1,0),(2,0),(-1,2),(2,-1)),
 ((0,0),(-1,0),(2,0),(-1,2),(2,-1)), ((0,0),(2,0),(-1,0),(2,1),(-1,-2)),
 ((0,0),(2,0),(-1,0),(2,1),(-1,-2)), ((0,0),(1,0),(-2,0),(1,-2),(-2,1)),
 ((0,0),(1,0),(-2,0),(1,-2),(-2,1)), ((0,0),(-2,0),(1,0),(-2,-1),(1,2)))

class Game:
    def __init__(self,seed=None,high_score=0):
        self.high_score=max(0,high_score);self.state=Screen.MENU;self.start_game(seed);self.state=Screen.MENU
    def start_game(self,seed=None):
        best=getattr(self,"high_score",0);self.board=Board();self.generator=PieceGenerator(seed)
        self.next_queue=[self.generator.next_piece() for _ in range(QUEUE_SIZE)]
        self.held=None;self.hold_used=False;self.score=0;self.lines=0;self.level=1;self.gravity_timer=0.0;self.events=[]
        self.active=self._take_next();self.state=Screen.PLAYING;self.high_score=best
        if not self.board.can_place(self.active):self._game_over()
    def _take_next(self):
        kind=self.next_queue.pop(0);self.next_queue.append(self.generator.next_piece());self.hold_used=False;return Piece(kind)
    @property
    def gravity_interval(self):return max(0.05,0.8-(self.level-1)*0.065)
    def add_score(self,points):
        if points>0:self.score+=points;self.high_score=max(self.high_score,self.score);self.events.append(("score",points))
    def move(self,dx,dy):
        if self.state!=Screen.PLAYING:return False
        p=self.active.copy();p.x+=dx;p.y+=dy
        if not self.board.can_place(p):return False
        self.active=p
        if dx:self.events.append(("move",None))
        return True
    def soft_drop(self):
        if not self.move(0,1):return False
        self.add_score(1);self.events.append(("soft_drop",None));return True
    def rotate(self,direction=1):
        if self.state!=Screen.PLAYING or not direction:return False
        if self.active.kind=="O":return True
        old=self.active.rotation%4;new=(old+(1 if direction>0 else -1))%4
        kicks=(I_KICKS if self.active.kind=="I" else JLSTZ)[old*2+(0 if direction>0 else 1)]
        for dx,dy in kicks:
            p=Piece(self.active.kind,self.active.x+dx,self.active.y+dy,new)
            if self.board.can_place(p):self.active=p;self.events.append(("rotate",None));return True
        return False
    def ghost_piece(self):
        ghost=self.active.copy()
        while self.board.can_place(Piece(ghost.kind,ghost.x,ghost.y+1,ghost.rotation)):ghost.y+=1
        return ghost
    def hard_drop(self):
        if self.state!=Screen.PLAYING:return 0
        distance=0
        while self.move(0,1):distance+=1
        self.add_score(distance*2);self.events.append(("hard_drop",None));self.lock_piece();return distance
    def hold_piece(self):
        if self.state!=Screen.PLAYING or self.hold_used:return False
        current=self.active.kind
        if self.held is None:self.held=current;self.active=self._take_next()
        else:
            swap=self.held;self.held=current;self.active=Piece(swap)
            if not self.board.can_place(self.active):self._game_over();return False
        self.hold_used=True;self.gravity_timer=0.0;self.events.append(("hold",None));return True
    def lock_piece(self):
        if self.state!=Screen.PLAYING:return 0
        if self.board.lock_piece(self.active):self._game_over();return 0
        self.events.append(("lock",None));rows=self.board.full_rows();cleared=self.board.clear_rows(rows)
        if cleared:
            self.add_score(LINE_POINTS[min(cleared,4)]*self.level);self.lines+=cleared;self.events.append(("clear",rows))
            if cleared==4:self.events.append(("tetris",None))
            old=self.level;self.level=1+self.lines//10
            if self.level>old:self.events.append(("level",self.level))
        self.active=self._take_next();self.gravity_timer=0.0
        if not self.board.can_place(self.active):self._game_over()
        return cleared
    def update(self,dt):
        if self.state!=Screen.PLAYING or dt<=0:return
        self.gravity_timer+=min(dt,0.25);interval=self.gravity_interval
        while self.gravity_timer>=interval and self.state==Screen.PLAYING:
            self.gravity_timer-=interval
            if not self.move(0,1):self.lock_piece();break
    def toggle_pause(self):
        if self.state==Screen.PLAYING:self.state=Screen.PAUSED
        elif self.state==Screen.PAUSED:self.state=Screen.PLAYING
    def _game_over(self):self.state=Screen.GAME_OVER;self.events.append(("game_over",None))
