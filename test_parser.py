import unittest
from parser import PuzzleParser
from visualizer import BoardVisualizer

class TestParser(unittest.TestCase):
    def test_parse_question_1(self):
        board, remaining = PuzzleParser.parse_file("questions/1.txt")
        
        print("Parsed Pieces:", list(board.placed_pieces.keys()))
        print("Remaining Pieces:", remaining)
        
        self.assertIn("Dog", board.placed_pieces)
        self.assertIn("Trainer", board.placed_pieces)
        self.assertIn("BlueBridge", board.placed_pieces)
        self.assertIn("OrangeTube", board.placed_pieces)
        self.assertIn("RedTube", board.placed_pieces)
        
        self.assertEqual(len(remaining), 3)
        self.assertIn("YellowSeesaw", remaining)
        self.assertIn("LightBlueHurdle", remaining)
        self.assertIn("PurpleHurdle", remaining)

        # Check coordinates (col, row)
        self.assertEqual(board.placed_pieces["Dog"][1:], (0, 0))
        self.assertEqual(board.placed_pieces["Trainer"][1:], (4, 4))
        self.assertEqual(board.placed_pieces["BlueBridge"][1:], (1, 1))
        self.assertEqual(board.placed_pieces["OrangeTube"][1:], (4, 2))
        self.assertEqual(board.placed_pieces["RedTube"][1:], (1, 3))

if __name__ == "__main__":
    unittest.main()
