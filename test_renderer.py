import unittest
from models import Board, Direction
from factory import PieceFactory
from visualizer import BoardVisualizer

class TestBoardRenderer(unittest.TestCase):
    def test_solution_1_full(self):
        """
        Verify Solution 1 from the manual.
        Uses the refactored factory which now supports connection-based routing.
        """
        board = Board()
        factory = PieceFactory()
        variants = factory.get_all_piece_variants()

        # Helper to find variant by ID
        def get_v(piece_id, variant_id):
            return next(v for v in variants[piece_id] if v.variant_id == f"{piece_id}{variant_id}")

        # Dog & Trainer
        board.place(get_v("Dog", ""), 0, 0)
        board.place(get_v("Trainer", ""), 4, 4)

        # Yellow Seesaw: Row 0, Col 2-4
        board.place(get_v("YellowSeesaw", "_Rot0"), 0, 2)

        # Blue Bridge: Row 1, Col 1-3
        board.place(get_v("BlueBridge", "_Rot0"), 1, 1)

        # Light Blue Hurdle: Row 2, Col 0-2
        board.place(get_v("LightBlueHurdle", "_Rot0"), 2, 0)

        # Orange Tube: Row 2, Col 4. Row 3, Col 4. Row 3, Col 3
        board.place(get_v("OrangeTube", "_Rot0"), 2, 4)

        # Red Tube: Row 3, Col 1. Row 4, Col 1
        board.place(get_v("RedTube", "_Rot0"), 3, 1)

        # Purple Hurdle: Row 4, Col 2-3
        board.place(get_v("PurpleHurdle", "_Rot0"), 4, 2)

        rendered = BoardVisualizer.render(board, with_indices=False)
        with open("expected_solution_1.txt", "r") as f:
            expected = f.read().strip()
        
        actual_lines = rendered.strip().split("\n")
        expected_lines = expected.split("\n")
        
        failures = []
        for r in range(5):
            for c in range(5):
                # Extract 3x3 block for cell (r, c)
                actual_block = []
                expected_block = []
                for sub_r in range(3):
                    line_idx = r * 4 + 1 + sub_r
                    actual_block.append(actual_lines[line_idx][c*4 + 1 : c*4 + 4])
                    expected_block.append(expected_lines[line_idx][c*4 + 1 : c*4 + 4])
                
                if actual_block != expected_block:
                    failures.append(f"Cell ({r},{c}) mismatch:\nExpected:\n" + "\n".join(expected_block) + 
                                   "\nActual:\n" + "\n".join(actual_block))
        
        if failures:
            print("\nActual Rendering (No Indices):")
            print(rendered)
            self.fail("\n\n" + "\n\n".join(failures))

if __name__ == "__main__":
    unittest.main()
