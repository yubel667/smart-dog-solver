import unittest
from models import Board, Direction
from factory import PieceFactory
from solver import Solver
from visualizer import BoardVisualizer

class TestSolver(unittest.TestCase):
    def test_solution_1_partial_initial_state(self):
        """
        Verify that the solver can find the full solution from a partial initial state.
        Initial state includes: Dog, Trainer, BlueBridge, OrangeTube, RedTube.
        Expected solution should also include: YellowSeesaw, LightBlueHurdle, PurpleHurdle.
        """
        board = Board()
        factory = PieceFactory()
        variants = factory.get_all_piece_variants()

        # Helper to find variant by ID
        def get_v(piece_id, variant_id):
            return next(v for v in variants[piece_id] if v.variant_id == f"{piece_id}{variant_id}")

        # Initial pieces (fixed in the puzzle)
        board.place(get_v("Dog", ""), 0, 0)
        board.place(get_v("Trainer", ""), 4, 4)
        board.place(get_v("BlueBridge", "_Rot0"), 1, 1)
        board.place(get_v("OrangeTube", "_Rot0"), 2, 4)
        board.place(get_v("RedTube", "_Rot0"), 3, 1)

        # Pieces for the solver to place
        remaining_pieces = ["YellowSeesaw", "LightBlueHurdle", "PurpleHurdle"]

        solver = Solver()
        result_board = solver.solve(board, remaining_pieces)

        self.assertIsNotNone(result_board, "Solver should find a solution.")

        # Check if all pieces are placed
        for piece_id in ["Dog", "Trainer", "BlueBridge", "OrangeTube", "RedTube", 
                        "YellowSeesaw", "LightBlueHurdle", "PurpleHurdle"]:
            self.assertIn(piece_id, result_board.placed_pieces, f"Piece {piece_id} should be placed.")

        # Check if the specific placements for the found pieces are correct
        # According to test_renderer.py:
        # Yellow Seesaw: Row 0, Col 2 (root_x, root_y)
        # Light Blue Hurdle: Row 2, Col 0 (root_x, root_y)
        # Purple Hurdle: Row 4, Col 2 (root_x, root_y)
        
        y_var, y_x, y_y = result_board.placed_pieces["YellowSeesaw"]
        lb_var, lb_x, lb_y = result_board.placed_pieces["LightBlueHurdle"]
        p_var, p_x, p_y = result_board.placed_pieces["PurpleHurdle"]

        # Note: (root_x, root_y) in our model maps to (col, row) if we think in (x, y) 
        # But in test_renderer.py: board.place(get_v("YellowSeesaw", "_Rot0"), 0, 2)
        # This seems to be (row, col) because Row 0, Col 2.
        # Let's verify Board.place(variant, root_x, root_y) in models.py
        # x, y = root_x + dx, root_y + dy
        # self.grid[x][y][level] = variant.piece_id
        # In test_renderer.py, it calls board.place(v, 0, 2) and says it's Row 0, Col 2.
        # So root_x is Row, root_y is Col.

        self.assertEqual(y_x, 0)
        self.assertEqual(y_y, 2)
        self.assertEqual(y_var.variant_id, "YellowSeesaw_Rot0")

        self.assertEqual(lb_x, 2)
        self.assertEqual(lb_y, 0)
        self.assertEqual(lb_var.variant_id, "LightBlueHurdle_Rot0")

        self.assertEqual(p_x, 4)
        self.assertEqual(p_y, 2)
        self.assertEqual(p_var.variant_id, "PurpleHurdle_Rot0")

if __name__ == "__main__":
    unittest.main()
