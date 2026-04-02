from typing import Tuple, List, Set, Dict, Optional
from models import Board, Direction, Level
from factory import PieceFactory

class PuzzleParser:
    SYMBOL_TO_ID = {
        "D": "Dog",
        "T": "Trainer",
        "O": "OrangeTube",
        "R": "RedTube",
        "B": "BlueBridge",
        "L": "LightBlueHurdle",
        "P": "PurpleHurdle",
        "Y": "YellowSeesaw"
    }

    @classmethod
    def parse_file(cls, file_path: str) -> Tuple[Board, List[str]]:
        """
        Parses a puzzle setup from a file.
        Returns a tuple of (Board with fixed pieces, List of remaining piece IDs).
        """
        with open(file_path, "r") as f:
            content = f.read()
        return cls.parse_string(content)

    @classmethod
    def parse_string(cls, content: str) -> Tuple[Board, List[str]]:
        """
        Parses a puzzle setup from a string.
        """
        lines = content.strip().split("\n")
        # Validate basic grid structure (5x5 cells, each cell is 3x3 chars + borders)
        # Expected lines: 5 cells * 3 lines + 6 separator lines = 21 lines
        if len(lines) != 21:
            raise ValueError(f"Invalid grid height: expected 21 lines, got {len(lines)}")

        board = Board()
        factory = PieceFactory()
        all_variants = factory.get_all_piece_variants()

        # Step 1: Extract symbols and connections for each cell
        grid_data = [[{"symbol": " ", "connections": set()} for _ in range(5)] for _ in range(5)]
        
        for r in range(5):
            for c in range(5):
                # Center of cell (r, c)
                center_line_idx = r * 4 + 2
                center_char_idx = c * 4 + 2
                
                # Scan 3x3 cell for symbols
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        char = lines[center_line_idx + dr][center_char_idx + dc]
                        if char in cls.SYMBOL_TO_ID:
                            # If we already found a symbol, we might have multiple pieces
                            # For now, let's store all found symbols in a list if needed
                            # But most logic expects one symbol per piece cell.
                            # In shared cells, we might have 'B' and 'O'.
                            # Let's use the center symbol if available, otherwise any found symbol.
                            if dr == 0 and dc == 0:
                                grid_data[r][c]["symbol"] = char
                            elif grid_data[r][c]["symbol"] == " ":
                                grid_data[r][c]["symbol"] = char
                            
                            # Handle shared cell: if we find both B and something else
                            # we should probably store both.
                            if "symbols" not in grid_data[r][c]:
                                grid_data[r][c]["symbols"] = set()
                            grid_data[r][c]["symbols"].add(char)

                if grid_data[r][c]["symbol"] == " " and "symbols" in grid_data[r][c]:
                    grid_data[r][c]["symbol"] = list(grid_data[r][c]["symbols"])[0]

                # Check connections
                # UP: char above center
                if lines[center_line_idx - 1][center_char_idx] in ["|", "B"]:
                    grid_data[r][c]["connections"].add(Direction.UP)
                # DOWN: char below center
                if lines[center_line_idx + 1][center_char_idx] in ["|", "B"]:
                    grid_data[r][c]["connections"].add(Direction.DOWN)
                # LEFT: char left of center
                if lines[center_line_idx][center_char_idx - 1] in ["-", "=", "B"]:
                    grid_data[r][c]["connections"].add(Direction.LEFT)
                # RIGHT: char right of center
                if lines[center_line_idx][center_char_idx + 1] in ["-", "=", "B"]:
                    grid_data[r][c]["connections"].add(Direction.RIGHT)

        # Step 2: Identify pieces and their root positions
        # A piece is a set of connected cells with the same symbol (or specific multi-cell logic)
        visited = set()
        placed_piece_ids = set()

        for r in range(5):
            for c in range(5):
                if (r, c) in visited or grid_data[r][c]["symbol"] == " ":
                    continue
                
                symbol = grid_data[r][c]["symbol"]
                piece_id = cls.SYMBOL_TO_ID.get(symbol)
                if not piece_id:
                    raise ValueError(f"Unknown symbol '{symbol}' at cell ({c}, {r})")

                # Find all cells belonging to this piece
                piece_cells = cls._find_connected_cells(grid_data, r, c, symbol)
                for pr, pc in piece_cells:
                    visited.add((pr, pc))

                # Identify the variant and root position
                match_found = False
                
                # In our coordinate system, x = col (pc), y = row (pr)
                # Sort piece_cells for consistent testing
                min_pc = min(pc for pr, pc in piece_cells)
                min_pr = min(pr for pr, pc in piece_cells)

                # Connection map for this piece instance relative to some root
                # We'll try each cell as a potential (0,0) of the variant's internal footprint
                for variant in all_variants[piece_id]:
                    # For a variant to match, its footprint must be able to cover piece_cells
                    # when translated by some (root_x, root_y)
                    # For each cell (v_dx, v_dy) in variant footprint, 
                    # try assuming it matches the first cell (pc0, pr0) of our piece
                    pc0, pr0 = piece_cells[0][1], piece_cells[0][0]
                    for v_dx0, v_dy0 in variant.footprint:
                        root_x = pc0 - v_dx0
                        root_y = pr0 - v_dy0
                        
                        # Proposed actual cells for this variant
                        actual_cells = {(root_x + dx, root_y + dy) for dx, dy in variant.footprint}
                        current_piece_cells = {(pc, pr) for pr, pc in piece_cells}
                        
                        if actual_cells == current_piece_cells:
                            # Footprint matches. Now check connections.
                            instance_conns = {}
                            for dx, dy in variant.footprint:
                                pc, pr = root_x + dx, root_y + dy
                                instance_conns[(dx, dy)] = grid_data[pr][pc]["connections"]
                            
                            if cls._matches_connections(variant, instance_conns):
                                if board.can_place(variant, root_x, root_y):
                                    board.place(variant, root_x, root_y)
                                    placed_piece_ids.add(piece_id)
                                    match_found = True
                                    break
                    if match_found: break
                
                if not match_found:
                    raise ValueError(f"Could not identify variant for piece '{piece_id}' at cells {piece_cells}")

        # Step 3: Determine remaining pieces
        all_required_pieces = ["OrangeTube", "RedTube", "BlueBridge", "LightBlueHurdle", "PurpleHurdle", "YellowSeesaw"]
        remaining_pieces = [p for p in all_required_pieces if p not in placed_piece_ids]
        
        return board, remaining_pieces

    @classmethod
    def _find_connected_cells(cls, grid_data, r, c, symbol) -> List[Tuple[int, int]]:
        cells = []
        stack = [(r, c)]
        visited = {(r, c)}
        while stack:
            curr_r, curr_c = stack.pop()
            cells.append((curr_r, curr_c))
            
            # For BlueBridge, connections might cross other symbols, but here we assume same symbol
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < 5 and 0 <= nc < 5 and (nr, nc) not in visited:
                    if symbol in grid_data[nr][nc].get("symbols", set()):
                        visited.add((nr, nc))
                        stack.append((nr, nc))
        return cells

    @classmethod
    def _matches_connections(cls, variant, instance_conns) -> bool:
        # For each square in the instance, its connections must match the variant's routing_info_at
        for (dx, dy), conns in instance_conns.items():
            required_conns = variant.routing_info_at(dx, dy)
            if not required_conns.issubset(conns):
                return False
        return True
