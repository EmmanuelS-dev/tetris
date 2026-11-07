from src.piece_generator import PieceGenerator
from src.tetromino import PIECE_TYPES


def test_each_seven_piece_bag_contains_every_type_once():
    generator = PieceGenerator(seed=42)
    pieces = [generator.next_piece() for _ in range(70)]
    for offset in range(0, len(pieces), 7):
        assert set(pieces[offset : offset + 7]) == set(PIECE_TYPES)


def test_seed_makes_randomizer_reproducible():
    left = PieceGenerator(seed=2025)
    right = PieceGenerator(seed=2025)
    assert [left.next_piece() for _ in range(28)] == [right.next_piece() for _ in range(28)]


def test_adjacent_bags_are_randomized():
    generator = PieceGenerator(seed=13)
    first = tuple(generator.next_piece() for _ in range(7))
    second = tuple(generator.next_piece() for _ in range(7))
    assert first != second
