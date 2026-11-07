from src.piece_generator import PieceGenerator
from src.tetromino import PIECE_TYPES

def test_each_bag_contains_each_piece_once():
    g=PieceGenerator(42);items=[g.next_piece() for _ in range(70)]
    for i in range(0,70,7):assert set(items[i:i+7])==set(PIECE_TYPES)
def test_seed_is_reproducible():
    a,b=PieceGenerator(2025),PieceGenerator(2025);assert [a.next_piece() for _ in range(35)]==[b.next_piece() for _ in range(35)]
