from src.tetromino import PIECE_TYPES,Piece,local_cells,piece_cells

def test_seven_shapes_are_four_cells():
    assert set(PIECE_TYPES)==set("IOTSZJL")
    assert all(len(local_cells(k))==4 for k in PIECE_TYPES)
def test_rotation_cycles_and_offsets():
    for k in PIECE_TYPES:assert set(local_cells(k,4))==set(local_cells(k,0))
    assert set(piece_cells(Piece("O",4,7)))=={(5,7),(6,7),(5,8),(6,8)}
