from src.config import BOARD_HEIGHT, BOARD_WIDTH
from src.game import Game
from src.tetromino import Piece


def prepare_clear(game: Game, count: int) -> None:
    first_row = BOARD_HEIGHT - count
    for y in range(first_row, BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            # The O piece fills the two missing cells in the bottom rows.
            if y < BOARD_HEIGHT - 2 or x not in (5, 6):
                game.board.grid[y][x] = "J"
    game.active = Piece("O", x=4, y=BOARD_HEIGHT - 2)


def test_single_double_triple_and_tetris_scoring():
    expected = (100, 300, 500, 800)
    for lines, base_points in enumerate(expected, start=1):
        game = Game(seed=1)
        game.start_game(seed=1)
        prepare_clear(game, lines)
        assert game.lock_piece() == lines
        assert game.score == base_points
        assert game.lines == lines


def test_clear_score_uses_level_before_progression():
    game = Game(seed=7)
    game.start_game(seed=7)
    game.lines = 9
    prepare_clear(game, 2)
    assert game.lock_piece() == 2
    assert game.score == 300
    assert game.lines == 11
    assert game.level == 2


def test_soft_and_hard_drop_points_are_per_cell():
    game = Game(seed=8)
    game.start_game(seed=8)
    game.active = Piece("O", x=3, y=5)
    assert game.soft_drop()
    assert game.score == 1
    assert game.hard_drop() == 12
    assert game.score == 25


def test_level_gravity_has_a_sensible_minimum():
    game = Game(seed=3)
    assert game.gravity_interval == 0.8
    game.level = 5
    assert game.gravity_interval < 0.8
    game.level = 99
    assert game.gravity_interval == 0.05
