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
        # Each cell (row, col) can have multiple pieces. 
        # We'll use a slightly more complex storage to handle multiple symbols.
        # cell_symbols[row][col] is a list of piece_ids
        cell_pieces = [[[] for _ in range(board.size)] for _ in range(board.size)]
        for piece_id, (variant, rx, ry) in board.placed_pieces.items():
            for (dx, dy) in variant.footprint:
                col, row = rx + dx, ry + dy
                cell_pieces[row][col].append((piece_id, variant, dx, dy))

        for row in range(board.size):
            for col in range(board.size):
                cx, cy = col * cell_size + 1, row * cell_size + 1
                pieces = cell_pieces[row][col]
                if not pieces:
                    continue
                
                # Sort pieces so Bridge is first (at center)
                pieces.sort(key=lambda x: 0 if x[1].is_bridge else 1)
                
                for i, (piece_id, variant, dx, dy) in enumerate(pieces):
                    symbol = cls.SYMBOLS.get(piece_id, "?")
                    if i == 0:
                        # Primary piece at center
                        canvas[cy][cx] = symbol
                    elif i == 1:
                        # Secondary piece at bottom-right
                        canvas[cy + 1][cx + 1] = symbol
                    
                    # Render connections
                    if symbol not in ["D", "T"]:
                        connections = variant.routing_info_at(dx, dy)
                        for d in connections:
                            dy_off, dx_off, char = DIR_MAP[d]
                            # Use '=' for bridge horizontal connections ONLY if square is shared
                            if variant.is_bridge and char == "-" and len(pieces) > 1:
                                char = "="
                            
                            # If we are the secondary piece, we don't want to overwrite 
                            # primary piece's connections unless necessary.
                            # But wait, shared cell rules: bridge and tunnel are orthogonal.
                            # So they won't share connection slots!
                            if i == 0:
                                canvas[cy + dy_off][cx + dx_off] = char
                            else:
                                # For secondary piece (Level 0), offset its connections if needed?
                                # Actually, standard diagrams just show them in their slots.
                                # UP/DOWN go to (cx, cy+/-1), LEFT/RIGHT go to (cx+/-1, cy).
                                # If those slots are free, use them.
                                if canvas[cy + dy_off][cx + dx_off] == " ":
                                    canvas[cy + dy_off][cx + dx_off] = char

        # 2. Assemble Rows
        output = []
        if with_indices:
            header = "     " + "   ".join(str(i) for i in range(board.size))
            output.append(header)
        
        sep = "+" + "---+" * board.size
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
