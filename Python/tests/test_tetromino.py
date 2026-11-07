from src.tetromino import PIECE_TYPES, Piece, local_cells, piece_cells


def test_all_seven_shapes_have_four_cells():
    assert set(PIECE_TYPES) == {"I", "O", "T", "S", "Z", "J", "L"}
    for kind in PIECE_TYPES:
        assert len(local_cells(kind)) == 4


def test_rotation_returns_to_original_occupancy_after_four_turns():
    for kind in PIECE_TYPES:
        assert set(local_cells(kind, 4)) == set(local_cells(kind, 0))


def test_piece_cells_apply_world_offset():
    piece = Piece("O", x=4, y=7)
    assert set(piece_cells(piece)) == {(5, 7), (6, 7), (5, 8), (6, 8)}
