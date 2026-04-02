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
    def render(cls, board: Board) -> str:
        """
        Renders the board using a 3x3 sub-grid per cell.
        Each cell center contains the piece ID letter.
        Edges contain path connection lines.
        """
        cell_size = 3
        canvas_size = board.size * cell_size
        canvas = [[" " for _ in range(canvas_size)] for _ in range(canvas_size)]

        # 1. Draw Pieces
        for piece_id, (variant, rx, ry) in board.placed_pieces.items():
            symbol = cls.SYMBOLS.get(piece_id, "?")
            
            for (dx, dy) in variant.footprint:
                x, y = rx + dx, ry + dy
                cx, cy = x * cell_size + 1, y * cell_size + 1
                
                # Center: Piece ID letter
                canvas[cy][cx] = symbol
                
                # Edges: Path connections (REMOVED)

        # 2. Assemble Output
        output = []
        # Header
        header = "      0     1     2     3     4"
        output.append(header)
        
        for y in range(board.size):
            output.append("   +---+---+---+---+---+")
            for sub_y in range(cell_size):
                line = f" {y if sub_y==1 else ' '} |"
                for x in range(board.size):
                    cell_content = "".join(canvas[y*cell_size + sub_y][x*cell_size : (x+1)*cell_size])
                    line += cell_content + "|"
                output.append(line)
        output.append("   +---+---+---+---+---+")

        return "\n".join(output)
