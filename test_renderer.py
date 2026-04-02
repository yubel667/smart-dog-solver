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
        # Manually add routing to Dog to exit RIGHT
        dog_v = PieceVariant("Dog", "Dog", {(0,0)}, {((0,0), Direction.RIGHT): ([(0,0, Level.GROUND)], Direction.RIGHT)})
        board.place(dog_v, 0, 0)
        
        # Manually add routing to Trainer to enter from UP
        trainer_v = PieceVariant("Trainer", "Trainer", {(0,0)}, {((0,0), Direction.UP): ([(0,0, Level.GROUND)], Direction.DOWN)})
        board.place(trainer_v, 4, 4)

        # Light Blue (E): (2,0) to (2,2). Vertical 1x3.
        lb_v = next(v for v in variants["LightBlueHurdle"] if v.variant_id == "LightBlueHurdle_Rot90")
        board.place(lb_v, 2, 0)

        # Blue Bridge (D): Corner (1,2), legs (2,2) and (1,3).
        # Footprint relative to (1,2): (0,0), (1,0), (0,1)
        blue_v = next(v for v in variants["BlueBridge"] if v.footprint == {(0,0), (1,0), (0,1)})
        board.place(blue_v, 1, 2)

        # Yellow (G): (0,2) to (0,4). Vertical 1x3. Turn RIGHT at (0,4).
        yellow_v = next(v for v in variants["YellowSeesaw"] if v.variant_id == "YellowSeesaw_ChiralA_Rot90")
        board.place(yellow_v, 0, 2)

        # Orange (C): Corner (3,4), legs (2,4) and (3,3).
        # Footprint relative to (3,4): (-1,0), (0,0), (0,-1)
        orange_v = next(v for v in variants["OrangeTube"] if v.footprint == {(-1,0), (0,0), (0,-1)})
        board.place(orange_v, 3, 4)

        # Red (H): Corner (4,1), Leg (3,1). 1x2 Curve.
        # Relative to (4,1): (-1,0), (0,0)
        red_v = next(v for v in variants["RedTube"] if v.footprint == {(-1,0), (0,0)} and v.variant_id.endswith("Rot180"))
        board.place(red_v, 4, 1)

        # Purple (F): (4,2) to (4,3). Vertical 1x2.
        purple_v = next(v for v in variants["PurpleHurdle"] if v.footprint == {(0,0), (0,1)})
        board.place(purple_v, 4, 2)

        rendered = BoardVisualizer.render(board)
        print("\nActual Rendering:")
        print(rendered)

        # Read expected
        with open("expected_solution_1.txt", "r") as f:
            expected = f.read()
        
        self.assertEqual(rendered.strip(), expected.strip())

if __name__ == "__main__":
    unittest.main()
