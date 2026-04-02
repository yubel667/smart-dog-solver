import unittest
from models import Board, Level, PieceVariant, Direction
from factory import PieceFactory
from visualizer import BoardVisualizer
import os

class TestBoardRenderer(unittest.TestCase):
    def test_solution_1_full(self):
        """
        Verify Solution 1 from the manual using the user's description.
        Dog (0,0), Trainer (4,4)
        Path: (0,0) -> (1,0) -> (2,0) [L-Blue] -> (2,2) -> (2,3) -> (1,3) [Bridge] -> (1,1) -> (0,1) -> (0,2) [Yellow] -> (0,4) -> (1,4) -> (2,4) [Orange] -> (3,4) -> (3,3) -> (3,2) -> (3,1) [Red] -> (4,1) -> (4,2) [Purple] -> (4,3) -> (4,4)
        """
        board = Board()
        factory = PieceFactory()
        variants = factory.get_all_piece_variants()

        # Dog & Trainer
        dog_v = PieceVariant("Dog", "Dog", {(0,0)}, {})
        board.place(dog_v, 0, 0)
        
        trainer_v = PieceVariant("Trainer", "Trainer", {(0,0)}, {})
        board.place(trainer_v, 4, 4)

        # Yellow (G): (0,2) to (0,4). Horizontal 1x3.
        # (0,2): -Y-, (0,3): -Y-, (0,4): -Y 
        yellow_v = PieceVariant("YellowSeesaw", "Yellow_Custom", {(0,0), (0,1), (0,2)}, {})
        # (0,2) needs Left and Right. Use entry Direction.DOWN (reverse UP=Left) and exit Direction.DOWN (Right).
        yellow_v.routing[((0,0), Direction.DOWN)] = ([(0,0, Level.GROUND)], Direction.DOWN)
        # (0,3) needs Left and Right.
        yellow_v.routing[((0,1), Direction.DOWN)] = ([(0,1, Level.GROUND)], Direction.DOWN)
        # (0,4) needs Left and Down. Use entry Direction.DOWN (Left) and exit Direction.RIGHT (Down).
        yellow_v.routing[((0,2), Direction.DOWN)] = ([(0,2, Level.GROUND)], Direction.RIGHT)
        board.place(yellow_v, 0, 2)

        # Blue Bridge (D): (1,1) to (1,3). 
        blue_v = PieceVariant("BlueBridge", "BlueBridge_Custom", {(0,0), (0,1), (0,2)}, {}, is_bridge=True)
        # (1,1) needs Right and Down. Use entry Direction.LEFT (reverse RIGHT=Down) and exit Direction.DOWN (Right).
        blue_v.routing[((0,0), Direction.LEFT)] = ([(0,0, Level.BRIDGE)], Direction.DOWN)
        # (1,2) needs Left and Right. Use entry Direction.DOWN (Left) and exit Direction.DOWN (Right).
        blue_v.routing[((0,1), Direction.DOWN)] = ([(0,1, Level.BRIDGE)], Direction.DOWN)
        # (1,3) needs Left and Down. Use entry Direction.DOWN (Left) and exit Direction.RIGHT (Down).
        blue_v.routing[((0,2), Direction.DOWN)] = ([(0,2, Level.BRIDGE)], Direction.RIGHT)
        board.place(blue_v, 1, 1)

        # Light Blue (E): (2,0) to (2,2). Horizontal 1x3.
        lb_v = PieceVariant("LightBlueHurdle", "LB_Custom", {(0,0), (0,1), (0,2)}, {})
        lb_v.routing[((0,0), Direction.DOWN)] = ([(0,0, Level.GROUND)], Direction.DOWN)
        lb_v.routing[((0,1), Direction.DOWN)] = ([(0,1, Level.GROUND)], Direction.DOWN)
        lb_v.routing[((0,2), Direction.DOWN)] = ([(0,2, Level.GROUND)], Direction.DOWN)
        board.place(lb_v, 2, 0)

        # Orange (C): (2,4), (3,4), (3,3). L-shape.
        orange_v = PieceVariant("OrangeTube", "Orange_Custom", {(0,0), (1,0), (1,-1)}, {})
        # (2,4) needs Up and Down. Use entry Direction.RIGHT (reverse LEFT=Up) and exit Direction.RIGHT (Down).
        orange_v.routing[((0,0), Direction.RIGHT)] = ([(0,0, Level.GROUND)], Direction.RIGHT)
        # (3,4) needs Up and Left. Use entry Direction.RIGHT (reverse LEFT=Up) and exit Direction.UP (Left).
        orange_v.routing[((1,0), Direction.RIGHT)] = ([(1,0, Level.GROUND)], Direction.UP)
        # (3,3) needs Up and Right. Use entry Direction.RIGHT (reverse LEFT=Up) and exit Direction.DOWN (Right).
        orange_v.routing[((1,-1), Direction.RIGHT)] = ([(1,-1, Level.GROUND)], Direction.DOWN)
        board.place(orange_v, 2, 4)

        # Red (H): (3,1), (4,1). Vertical 1x2.
        red_v = PieceVariant("RedTube", "Red_Custom", {(0,0), (1,0)}, {})
        # (3,1) needs Up and Down. Use entry Direction.RIGHT (Up) and exit Direction.RIGHT (Down).
        red_v.routing[((0,0), Direction.RIGHT)] = ([(0,0, Level.GROUND)], Direction.RIGHT)
        # (4,1) needs Up and Right. Use entry Direction.RIGHT (Up) and exit Direction.DOWN (Right).
        red_v.routing[((1,0), Direction.RIGHT)] = ([(1,0, Level.GROUND)], Direction.DOWN)
        board.place(red_v, 3, 1)

        # Purple (F): (4,2), (4,3). Horizontal 1x2.
        purple_v = PieceVariant("PurpleHurdle", "Purple_Custom", {(0,0), (0,1)}, {})
        purple_v.routing[((0,0), Direction.DOWN)] = ([(0,0, Level.GROUND)], Direction.DOWN)
        purple_v.routing[((0,1), Direction.DOWN)] = ([(0,1, Level.GROUND)], Direction.DOWN)
        board.place(purple_v, 4, 2)


        rendered = BoardVisualizer.render(board, with_indices=False)
        print("\nActual Rendering (No Indices):")
        print(rendered)

        # Read expected
        with open("expected_solution_1.txt", "r") as f:
            expected = f.read()
        
        # Cell-by-cell comparison
        actual_lines = rendered.strip().split("\n")
        expected_lines = expected.strip().split("\n")
        
        self.assertEqual(len(actual_lines), len(expected_lines), f"Line count mismatch: {len(actual_lines)} vs {len(expected_lines)}")
        
        failures = []
        for r in range(5):
            for c in range(5):
                # Extract 3x3 block for cell (r, c)
                actual_block = []
                expected_block = []
                for sub_r in range(3):
                    line_idx = r * 4 + 1 + sub_r
                    # Characters are at c*4 + 1, c*4 + 2, c*4 + 3
                    actual_block.append(actual_lines[line_idx][c*4 + 1 : c*4 + 4])
                    expected_block.append(expected_lines[line_idx][c*4 + 1 : c*4 + 4])
                
                if actual_block != expected_block:
                    failures.append(f"Cell ({r},{c}) mismatch:\nExpected:\n" + "\n".join(expected_block) + 
                                   "\nActual:\n" + "\n".join(actual_block))
        
        if failures:
            self.fail("\n\n" + "\n\n".join(failures))

if __name__ == "__main__":
    unittest.main()
