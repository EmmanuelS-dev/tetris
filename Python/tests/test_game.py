from src.game import Game,Screen
from src.tetromino import Piece

def prepare_clear(g,n):
    for y in range(20-n,20):
        for x in range(10):
            if y<18 or x not in (5,6):g.board.grid[y][x]="J"
    g.active=Piece("O",4,18)
def test_movement_rotation_wall_kick_and_ghost():
    g=Game(2);g.start_game(2);g.active=Piece("T",3,5);assert g.move(-1,0);assert g.rotate(1) and g.active.rotation==1
    g.active=Piece("I",-1,5,1);assert g.rotate(-1) and (g.active.rotation,g.active.x)==(0,1)
    g.active=Piece("O",3,-1);assert g.ghost_piece().y==18;g.board.grid[19][4]="J";assert g.ghost_piece().y==17
def test_gravity_and_drop_scoring():
    g=Game(8);g.start_game(8);g.active=Piece("O",3,5)
    assert g.soft_drop() and g.score==1;assert g.hard_drop()==12 and g.score==25
    g.active=Piece("O",3,5);start=g.active.y;g.gravity_timer=0
    for _ in range(3):g.update(.2)
    assert g.active.y==start;g.update(.2);assert g.active.y==start+1
def test_line_scores_levels_and_tetris():
    for n,score in enumerate((100,300,500,800),1):
        g=Game(1);g.start_game(1);prepare_clear(g,n);assert g.lock_piece()==n;assert g.score==score and g.lines==n
    g=Game(7);g.start_game(7);g.lines=9;prepare_clear(g,2);assert g.lock_piece()==2;assert g.score==300 and g.level==2
    g.level=99;assert g.gravity_interval==.05
def test_hold_once_per_piece_and_resets_on_lock():
    g=Game(9);g.start_game(9);first=g.active.kind;assert g.hold_piece() and g.held==first;assert not g.hold_piece()
    g.hard_drop();current=g.active.kind;assert g.hold_piece() and g.active.kind==first and g.held==current
def test_gameover_pause_restart():
    g=Game(4);g.start_game(4);g.active=Piece("T",3,-2);g.lock_piece();assert g.state==Screen.GAME_OVER
    g.start_game(4);g.toggle_pause();y=g.active.y;g.update(1);assert g.active.y==y and g.state==Screen.PAUSED
    g.start_game(4);assert g.state==Screen.PLAYING
