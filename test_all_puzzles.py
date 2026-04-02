import unittest
import os
from parser import PuzzleParser
from solver import Solver
from visualizer import BoardVisualizer

class TestAllPuzzles(unittest.TestCase):
    def test_all_questions(self):
        questions_dir = "questions"
        solutions_dir = "solutions"
        
        # Get all .txt files in questions/
        question_files = sorted([f for f in os.listdir(questions_dir) if f.endswith(".txt")])
        
        for q_file in question_files:
            puzzle_num = q_file.split(".txt")[0]
            with self.subTest(puzzle=puzzle_num):
                q_path = os.path.join(questions_dir, q_file)
                s_path = os.path.join(solutions_dir, q_file)
                
                # 1. Parse Question
                board, remaining = PuzzleParser.parse_file(q_path)
                
                # 2. Solve
                solver = Solver()
                result = solver.solve(board, remaining)
                self.assertIsNotNone(result, f"Puzzle {puzzle_num} should have a solution.")
                
                result_board, _ = result
                
                # 3. Compare with Expected Solution
                actual_render = BoardVisualizer.render(result_board, with_indices=False)
                
                if not os.path.exists(s_path):
                    self.fail(f"Solution file {s_path} missing.")
                
                with open(s_path, "r") as f:
                    expected_render = f.read().strip()
                
                # Compare cell by cell to give better error messages
                actual_lines = actual_render.strip().split("\n")
                expected_lines = expected_render.split("\n")
                
                self.assertEqual(len(actual_lines), len(expected_lines), f"Puzzle {puzzle_num} height mismatch.")
                
                for r, (actual_line, expected_line) in enumerate(zip(actual_lines, expected_lines)):
                    self.assertEqual(actual_line, expected_line, f"Puzzle {puzzle_num} mismatch at line {r}:\nActual:   {actual_line}\nExpected: {expected_line}")

if __name__ == "__main__":
    unittest.main()
