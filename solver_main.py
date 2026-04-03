import sys
import os
from parser import PuzzleParser
from solver import Solver
from visualizer import BoardVisualizer

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 solver_main.py <puzzle_number> [-v]")
        sys.exit(1)

    puzzle_num = sys.argv[1]
    if puzzle_num[0] == "s":
        file_path = f"solutions/{puzzle_num[1:]}.txt"
    else:
        file_path = f"questions/{puzzle_num}.txt"
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    if not os.path.exists(file_path):
        print(f"Error: Puzzle file {file_path} not found.")
        sys.exit(1)

    try:
        print(f"--- Parsing Puzzle {puzzle_num} ---")
        board, remaining_pieces = PuzzleParser.parse_file(file_path)
        
        print(f"Fixed pieces: {list(board.placed_pieces.keys())}")
        print(f"Pieces to place: {remaining_pieces}")
        
        solver = Solver()
        print("--- Solving ---")
        result = solver.solve(board, remaining_pieces, verbose=verbose)

        if result:
            result_board, path = result
            print("--- Solution Found ---")
            print(BoardVisualizer.render(result_board))
            print("\n--- Obstacle Moving Order ---")
            obstacles = []
            for _, _, p_id in path:
                if p_id and (not obstacles or obstacles[-1] != p_id):
                    obstacles.append(p_id)
            print(" -> ".join(obstacles))
        else:
            print("No solution found.")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
