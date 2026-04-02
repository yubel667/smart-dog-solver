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
        Renders the board using a 3x3 sub-grid per cell.
        Transposes X and Y so that board.place(v, x, y) uses x as Row and y as Column.
        Each cell center contains the piece ID letter.
        Edges contain path connection lines (- and |).
        """
        cell_size = 3
        canvas_size = board.size * cell_size
        canvas = [[" " for _ in range(canvas_size)] for _ in range(canvas_size)]

        # 1. Draw Pieces and Connections
        for piece_id, (variant, rx, ry) in board.placed_pieces.items():
            symbol = cls.SYMBOLS.get(piece_id, "?")
            
            for (dx, dy) in variant.footprint:
                # Transpose: rx is row, ry is col
                row, col = rx + dx, ry + dy
                cx, cy = col * cell_size + 1, row * cell_size + 1
                
                # Center: Piece ID letter
                canvas[cy][cx] = symbol
                
                # Edges: Path connections (only for obstacles, not Dog/Trainer)
                if symbol not in ["D", "T"]:
                    connections = variant.routing_info_at(dx, dy)
                    for d in connections:
                        if d == Direction.UP: # dy=-1 -> Left
                            canvas[cy][cx - 1] = "-"
                        elif d == Direction.DOWN: # dy=1 -> Right
                            canvas[cy][cx + 1] = "-"
                        elif d == Direction.LEFT: # dx=-1 -> Up
                            canvas[cy - 1][cx] = "|"
                        elif d == Direction.RIGHT: # dx=1 -> Down
                            canvas[cy + 1][cx] = "|"

        # 2. Assemble Output
        output = []
        if with_indices:
            # Header
            header = "      0     1     2     3     4"
            output.append(header)
        
        for r in range(board.size):
            if with_indices:
                output.append("   +---+---+---+---+---+")
            else:
                output.append("+---+---+---+---+---+")
            for sub_y in range(cell_size):
                if with_indices:
                    line = f" {r if sub_y==1 else ' '} |"
                else:
                    line = "|"
                for c in range(board.size):
                    cell_content = "".join(canvas[r*cell_size + sub_y][c*cell_size : (c+1)*cell_size])
                    line += cell_content + "|"
                output.append(line)
        
        if with_indices:
            output.append("   +---+---+---+---+---+")
        else:
            output.append("+---+---+---+---+---+")

        return "\n".join(output)
