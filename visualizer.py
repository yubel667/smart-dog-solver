from models import Board, Level, Direction
from typing import List, Tuple, Set

class BoardVisualizer:
    # Map piece IDs to short 1-character symbols for display
    SYMBOLS = {
        "OrangeTube": "O",
        "RedTube": "R",
        "BlueBridge": "B",
        "LightBlueHurdle": "L",
        "PurpleHurdle": "P",
        "YellowSeesaw": "Y",
        "Dog": "D",
        "Trainer": "T"
    }

    @classmethod
    def render(cls, board: Board, with_indices: bool = True) -> str:
        """
        Renders the 5x5 board into a string representation.
        
        Args:
            board: The board to render.
            with_indices: If True, include row/column indices and extra spacing.
        
        Note: The rendering transposes X and Y so that board.place(v, x, y) 
              treats x as the Row and y as the Column.
        """
        cell_size = 3
        canvas_size = board.size * cell_size
        canvas = [[" " for _ in range(canvas_size)] for _ in range(canvas_size)]

        # Map Direction to sub-grid offset and character
        # UP    (0, -1) -> Row delta -1, Col delta 0
        # DOWN  (0, 1)  -> Row delta 1, Col delta 0
        # LEFT  (-1, 0) -> Row delta 0, Col delta -1
        # RIGHT (1, 0)  -> Row delta 0, Col delta 1
        DIR_MAP = {
            Direction.UP:    (-1, 0, "|"),
            Direction.DOWN:  (1, 0,  "|"),
            Direction.LEFT:  (0, -1, "-"),
            Direction.RIGHT: (0, 1,  "-")
        }

        # 1. Fill Canvas
        for piece_id, (variant, rx, ry) in board.placed_pieces.items():
            symbol = cls.SYMBOLS.get(piece_id, "?")
            
            for (dx, dy) in variant.footprint:
                # No transpose: rx is col, ry is row
                col, row = rx + dx, ry + dy
                # Sub-grid center: cy is row-major y, cx is col-major x
                cx, cy = col * cell_size + 1, row * cell_size + 1
                
                canvas[cy][cx] = symbol
                
                # Render connections for non-endpoint pieces
                if symbol not in ["D", "T"]:
                    connections = variant.routing_info_at(dx, dy)
                    for d in connections:
                        dy_off, dx_off, char = DIR_MAP[d]
                        canvas[cy + dy_off][cx + dx_off] = char

        # 2. Assemble Rows
        output = []
        if with_indices:
            output.append("      0     1     2     3     4")
        
        sep = "+---+---+---+---+---+"
        margin = "   " if with_indices else ""
        
        for r in range(board.size):
            output.append(f"{margin}{sep}")
            for sub_y in range(cell_size):
                if with_indices:
                    label = f" {r} " if sub_y == 1 else "   "
                    line = f"{label}|"
                else:
                    line = "|"
                
                for c in range(board.size):
                    cell_chars = canvas[r * cell_size + sub_y][c * cell_size : (c + 1) * cell_size]
                    line += "".join(cell_chars) + "|"
                output.append(line)
        
        output.append(f"{margin}{sep}")
        return "\n".join(output)
