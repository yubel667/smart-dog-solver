import unittest
from models import Board, PieceVariant, Direction, Level
from visualizer import BoardVisualizer

class TestBoardRenderer(unittest.TestCase):
    def test_solution_1_full(self):
        board = Board()
        
        # Helper to create a custom variant for a single placement
        def place_custom(piece_id, root_x, root_y, footprint, connections_map, is_bridge=False):
            routing = {}
            for coord, dirs in connections_map.items():
                # We use a dummy entry to trigger the routing_info_at logic
                # For each square, we can add a path that contains just that square
                # with entry/exit dirs that produce the desired connections.
                # DIR_MAP: UP=Left, DOWN=Right, LEFT=Up, RIGHT=Down
                for d in dirs:
                    routing[(coord, d.reverse())] = ([(coord[0], coord[1], Level.BRIDGE if is_bridge else Level.GROUND)], d)
            
            v = PieceVariant(piece_id, piece_id, footprint, routing, is_bridge=is_bridge)
            board.place(v, root_x, root_y)

        # Dog & Trainer
        place_custom("Dog", 0, 0, {(0,0)}, {})
        place_custom("Trainer", 4, 4, {(0,0)}, {})

        # Yellow Seesaw: (0,2)-(0,4)
        # (0,2): -Y-, (0,3): -Y-, (0,4): -Y and | below
        place_custom("YellowSeesaw", 0, 2, {(0,0), (0,1), (0,2)}, {
            (0,0): {Direction.UP, Direction.DOWN},
            (0,1): {Direction.UP, Direction.DOWN},
            (0,2): {Direction.UP, Direction.RIGHT}
        })

        # Blue Bridge: (1,1)-(1,3)
        # (1,1): B- and | below, (1,2): -B-, (1,3): -B and | below
        place_custom("BlueBridge", 1, 1, {(0,0), (0,1), (0,2)}, {
            (0,0): {Direction.DOWN, Direction.RIGHT},
            (0,1): {Direction.UP, Direction.DOWN},
            (0,2): {Direction.UP, Direction.RIGHT}
        }, is_bridge=True)

        # Light Blue: (2,0)-(2,2)
        # -L- for all
        place_custom("LightBlueHurdle", 2, 0, {(0,0), (0,1), (0,2)}, {
            (0,0): {Direction.UP, Direction.DOWN},
            (0,1): {Direction.UP, Direction.DOWN},
            (0,2): {Direction.UP, Direction.DOWN}
        })

        # Orange Tube: (2,4), (3,4), (3,3)
        # (2,4): O and | above and below
        # (3,4): -O and | above
        # (3,3): O- and | above
        place_custom("OrangeTube", 2, 4, {(0,0), (1,0), (1,-1)}, {
            (0,0): {Direction.LEFT, Direction.RIGHT},
            (1,0): {Direction.UP, Direction.LEFT},
            (1,-1): {Direction.DOWN, Direction.LEFT}
        })

        # Red Tube: (3,1), (4,1)
        # (3,1): R and | above and below
        # (4,1): R- and | above
        place_custom("RedTube", 3, 1, {(0,0), (1,0)}, {
            (0,0): {Direction.LEFT, Direction.RIGHT},
            (1,0): {Direction.DOWN, Direction.LEFT}
        })

        # Purple Hurdle: (4,2)-(4,3)
        # -P- for all
        place_custom("PurpleHurdle", 4, 2, {(0,0), (0,1)}, {
            (0,0): {Direction.UP, Direction.DOWN},
            (0,1): {Direction.UP, Direction.DOWN}
        })

        rendered = BoardVisualizer.render(board, with_indices=False)
        with open("expected_solution_1.txt", "r") as f:
            expected = f.read().strip()
        
        actual_lines = rendered.strip().split("\n")
        expected_lines = expected.split("\n")
        
        failures = []
        for r in range(5):
            for c in range(5):
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
