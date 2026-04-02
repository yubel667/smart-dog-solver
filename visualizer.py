from models import Board, Level, Direction
from typing import List, Tuple

class BoardVisualizer:
    # ANSI Color codes for pieces
    COLORS = {
        "OrangeTube": "\033[38;5;208m",
        "RedTube": "\033[31m",
        "BlueBridge": "\033[34m",
        "LightBlueHurdle": "\033[36m",
        "PurpleHurdle": "\033[35m",
        "YellowSeesaw": "\033[33m",
        "Dog": "\033[1;32m",
        "Trainer": "\033[1;31m",
        "Path": "\033[90m", # Gray for empty square paths
        "RESET": "\033[0m"
    }

    @classmethod
    def render(cls, board: Board) -> str:
        """
        Renders the board using a 3x3 sub-grid per cell for high-fidelity path visualization.
        """
        # 5x5 cells -> 15x15 characters
        canvas_size = board.size * 3
        canvas = [[" " for _ in range(canvas_size)] for _ in range(canvas_size)]
        colors = [[cls.COLORS["RESET"] for _ in range(canvas_size)] for _ in range(canvas_size)]

        # 1. Draw Grid Lines
        for i in range(board.size + 1):
            for j in range(canvas_size):
                # Vertical grid lines
                if i * 3 < canvas_size:
                    pass # We'll draw borders later for clarity

        # 2. Draw Pieces
        for piece_id, (variant, rx, ry) in board.placed_pieces.items():
            color = cls.COLORS.get(piece_id, cls.COLORS["RESET"])
            
            if piece_id in ["Dog", "Trainer"]:
                canvas[ry*3+1][rx*3+1] = "D" if piece_id == "Dog" else "T"
                colors[ry*3+1][rx*3+1] = color
                continue

            # Draw the tracks for this piece
            for (dx, dy), box_char in variant.char_map.items():
                x, y = rx + dx, ry + dy
                cx, cy = x * 3 + 1, y * 3 + 1
                canvas[cy][cx] = box_char
                colors[cy][cx] = color
                
                # Fill connections to sub-grid edges
                dirs = variant.routing_info_at(dx, dy) # We'll add this helper to Variant
                for d in dirs:
                    sx, sy = cx + d.dx, cy + d.dy
                    canvas[sy][sx] = "┃" if d in [Direction.UP, Direction.DOWN] else "━"
                    if variant.is_bridge:
                        canvas[sy][sx] = "║" if d in [Direction.UP, Direction.DOWN] else "═"
                    colors[sy][sx] = color

        # 3. Assemble Output
        output = []
        # Header
        output.append("      " + "     ".join(str(i) for i in range(board.size)))
        
        for y in range(board.size):
            output.append("   " + "+---" * board.size + "+")
            for sub_y in range(3):
                line = f" {y if sub_y==1 else ' '} |"
                for x in range(board.size):
                    cell_content = ""
                    for sub_x in range(3):
                        char = canvas[y*3 + sub_y][x*3 + sub_x]
                        color = colors[y*3 + sub_y][x*3 + sub_x]
                        cell_content += color + char + cls.COLORS["RESET"]
                    line += cell_content + "|"
                output.append(line)
        output.append("   " + "+---" * board.size + "+")

        return "\n".join(output)

# Update models.py with routing_info_at
