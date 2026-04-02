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
        dog_v = PieceVariant("Dog", "Dog", {(0,0)}, {((0,0), Direction.RIGHT): ([(0,0, Level.GROUND)], Direction.RIGHT)})
        board.place(dog_v, 0, 0)
        
        trainer_v = PieceVariant("Trainer", "Trainer", {(0,0)}, {((0,0), Direction.UP): ([(0,0, Level.GROUND)], Direction.DOWN)})
        board.place(trainer_v, 4, 4)

        # Yellow (G): (0,2) to (0,4). Horizontal 1x3.
        # Chiral B Rot90 at (0,2) gives (0,2),(0,3),(0,4) and turns DOWN at end.
        yellow_v = next(v for v in variants["YellowSeesaw"] if v.variant_id == "YellowSeesaw_ChiralB_Rot90")
        board.place(yellow_v, 0, 2)

        # Blue Bridge (D): (1,1) to (1,3). 
        # Using a custom 1x3 bridge to match the expected output.
        blue_v = PieceVariant("BlueBridge", "BlueBridge_Custom", 
                              {(0,0), (0,1), (0,2)}, 
                              {((0,0), Direction.DOWN): ([(0,0, Level.BRIDGE), (0,1, Level.BRIDGE), (0,2, Level.BRIDGE)], Direction.DOWN)},
                              is_bridge=True)
        # Add tunnel connections for '|' below (Direction.RIGHT is DOWN in row,col)
        blue_v.routing[((0,0), Direction.RIGHT)] = ([(0,0, Level.GROUND)], Direction.RIGHT)
        blue_v.routing[((0,2), Direction.RIGHT)] = ([(0,2, Level.GROUND)], Direction.RIGHT)
        board.place(blue_v, 1, 1)

        # Light Blue (E): (2,0) to (2,2). Horizontal 1x3.
        lb_v = next(v for v in variants["LightBlueHurdle"] if v.variant_id == "LightBlueHurdle_Rot90")
        board.place(lb_v, 2, 0)

        # Orange (C): (2,4), (3,4), (3,3). L-shape.
        # Rot180 of footprint {(0,0), (1,0), (0,1)} is {(0,0), (-1,0), (0,-1)}
        orange_v = next(v for v in variants["OrangeTube"] if v.variant_id == "OrangeTube_Rot180")
        board.place(orange_v, 3, 4)

        # Red (H): (3,1), (4,1). Vertical 1x2.
        # Rot90 gives exit DOWN (RIGHT in (row,col))
        red_v = next(v for v in variants["RedTube"] if v.variant_id == "RedTube_Rot90")
        board.place(red_v, 4, 1)

        # Purple (F): (4,2), (4,3). Horizontal 1x2.
        purple_v = next(v for v in variants["PurpleHurdle"] if v.variant_id == "PurpleHurdle_Rot90")
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
