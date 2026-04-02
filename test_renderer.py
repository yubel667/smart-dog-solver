import unittest
from models import Board, Level, PieceVariant
from factory import PieceFactory
from visualizer import BoardVisualizer

class TestBoardRenderer(unittest.TestCase):
    def test_solution_1_full(self):
        """
        Verify Solution 1 from the manual.
        Dog at (0,0), Trainer at (4,4)
        Path: Dog -> (1,0)-(3,0) [Yellow] -> (3,1)-(4,1) [Red] -> (4,2)-(4,3) [Purple] -> Trainer
        This is a partial set of pieces to verify the renderer.
        """
        board = Board()
        factory = PieceFactory()
        variants = factory.get_all_piece_variants()

        # Dog & Trainer
        board.place(PieceVariant("Dog", "Dog", {(0,0)}, {}), 0, 0)
        board.place(PieceVariant("Trainer", "Trainer", {(0,0)}, {}), 4, 4)

        # Yellow (G): (1,0) to (3,0). Rot0 Chiral A.
        # Enter (1,0) from LEFT, exit (3,0) DOWN.
        yellow_v = next(v for v in variants["YellowSeesaw"] if v.variant_id == "YellowSeesaw_ChiralA_Rot0")
        board.place(yellow_v, 1, 0)

        # Red (H): Corner (4,1), Leg (3,1).
        # Relative to (4,1): (-1,0), (0,0). Rot 180 or similar.
        # Target: Enter (3,1) from LEFT, turn at (4,1) DOWN.
        red_v = next(v for v in variants["RedTube"] if v.footprint == {(-1,0), (0,0)})
        # Footprint {(-1,0), (0,0)} corresponds to Rot180 of our base {(0,0), (1,0)}
        board.place(red_v, 4, 1)

        # Purple (F): (4,2) to (4,3). Vertical 1x2.
        purple_v = next(v for v in variants["PurpleHurdle"] if v.footprint == {(0,0), (0,1)})
        board.place(purple_v, 4, 2)

        # Blue Bridge (D): Corner (1,1), legs (2,1) and (1,2)
        # Footprint relative to (1,1): (0,0), (1,0), (0,1)
        blue_v = next(v for v in variants["BlueBridge"] if v.footprint == {(0,0), (1,0), (0,1)})
        board.place(blue_v, 1, 1)

        # Light Blue (E): (0,1), (0,2), (0,3). Vertical 1x3.
        lb_v = next(v for v in variants["LightBlueHurdle"] if v.footprint == {(0,0), (0,1), (0,2)})
        board.place(lb_v, 0, 1)

        print("\nSolution 1 Partial Rendering:")
        print(BoardVisualizer.render(board))

if __name__ == "__main__":
    unittest.main()
