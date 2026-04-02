import unittest
from models import Board, Direction
from factory import PieceFactory
from solver import Solver
from visualizer import BoardVisualizer

class TestSolver(unittest.TestCase):
    def test_solution_1_full_state_pathing(self):
        """
        Verify that the solver can find the path when ALL pieces are already placed.
        """
        board = Board()
        factory = PieceFactory()
        variants = factory.get_all_piece_variants()

        def get_v(piece_id, variant_id):
            return next(v for v in variants[piece_id] if v.variant_id == f"{piece_id}{variant_id}")

        board.place(get_v("Dog", ""), 0, 0)
        board.place(get_v("Trainer", ""), 4, 4)
        board.place(get_v("YellowSeesaw", "_Rot0"), 0, 2)
        board.place(get_v("BlueBridge", "_Rot0"), 1, 1)
        board.place(get_v("LightBlueHurdle", "_Rot0"), 2, 0)
        board.place(get_v("OrangeTube", "_Rot0"), 2, 4)
        board.place(get_v("RedTube", "_Rot0"), 3, 1)
        board.place(get_v("PurpleHurdle", "_Rot0"), 4, 2)

        solver = Solver()
        # remaining_pieces is empty because all are placed
        result_board = solver.solve(board, [])

        self.assertIsNotNone(result_board, "Solver should find the path for the full solution.")

if __name__ == "__main__":
    unittest.main()
