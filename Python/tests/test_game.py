from src.game import Game, Screen
from src.tetromino import Piece


def test_move_rotation_and_wall_kick():
    game = Game(seed=2)
    game.start_game(seed=2)
    game.active = Piece("T", x=3, y=5)
    assert game.move(-1, 0)
    assert game.rotate(1)
    assert game.active.rotation == 1
    game.active = Piece("I", x=-1, y=5, rotation=1)
    assert game.rotate(-1)
    assert (game.active.rotation, game.active.x) == (0, 1)


def test_ghost_piece_lands_on_floor_and_stack():
    game = Game(seed=5)
    game.start_game(seed=5)
    game.active = Piece("O", x=3, y=-1)
    ghost = game.ghost_piece()
    assert ghost.y == 18
    game.board.grid[19][4] = "J"
    assert game.ghost_piece().y == 17


def test_gravity_uses_elapsed_time_and_locks_on_contact():
    game = Game(seed=1)
    game.start_game(seed=1)
    start_y = game.active.y
    for _ in range(3):
        game.update(0.2)
    assert game.active.y == start_y
    game.update(0.2)
    assert game.active.y == start_y + 1
    game.active = Piece("O", x=3, y=18)
    for _ in range(4):
        game.update(0.2)
    assert game.board.grid[18][4] == "O"
    assert game.board.grid[19][5] == "O"


def test_hold_is_once_per_piece_and_resets_after_lock():
    game = Game(seed=9)
    game.start_game(seed=9)
    first = game.active.kind
    assert game.hold_piece()
    assert game.held == first
    assert not game.hold_piece()
    next_kind = game.active.kind
    game.hard_drop()
    assert game.hold_piece()
    assert game.active.kind == first
    assert game.held == next_kind


def test_game_over_on_lock_above_visible_board():
    game = Game(seed=4)
    game.start_game(seed=4)
    game.active = Piece("T", x=3, y=-2)
    game.lock_piece()
    assert game.state == Screen.GAME_OVER


def test_pause_freezes_game_and_restart_returns_to_playing():
    game = Game(seed=2)
    game.start_game(seed=2)
    game.toggle_pause()
    start_y = game.active.y
    game.update(0.25)
    assert game.active.y == start_y
    assert game.state == Screen.PAUSED
    game.start_game(seed=2)
    assert game.state == Screen.PLAYING
