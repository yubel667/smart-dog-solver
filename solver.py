import math
from models import Board, Direction, Level, PieceVariant
from factory import PieceFactory

class Solver:
    def __init__(self, print_factor=1.5):
        self.factory = PieceFactory()
        self.all_variants = self.factory.get_all_piece_variants()
        self.print_factor = print_factor
        self.verbose = False
        self.visited_count = 0
        self.next_print_n = 1
        
        self.piece_ports_base = {
            "OrangeTube": {
                (0,0): {Direction.UP, Direction.DOWN},
                (0,1): {Direction.UP, Direction.LEFT},
                (-1,1): {Direction.RIGHT, Direction.UP}
            },
            "RedTube": {
                (0,0): {Direction.UP, Direction.DOWN},
                (0,1): {Direction.UP, Direction.RIGHT},
                (1,1): {Direction.UP, Direction.LEFT}
            },
            "BlueBridge": {
                (0,0): {Direction.RIGHT, Direction.DOWN},
                (1,0): {Direction.LEFT, Direction.RIGHT},
                (2,0): {Direction.LEFT, Direction.DOWN}
            },
            "LightBlueHurdle": {
                (0,0): set(),
                (1,0): {Direction.UP, Direction.DOWN},
                (2,0): set()
            },
            "PurpleHurdle": {
                (0,0): {Direction.LEFT, Direction.RIGHT},
                (1,0): {Direction.LEFT, Direction.RIGHT}
            },
            "YellowSeesaw": {
                (0,0): {Direction.LEFT, Direction.RIGHT},
                (1,0): {Direction.LEFT, Direction.RIGHT},
                (2,0): {Direction.LEFT, Direction.DOWN}
            },
            "Dog": {(0,0): set()},
            "Trainer": {(0,0): set()}
        }
        
        self.variant_ports = {}
        self.yellow_entries = {}
        
        for p_id, variants in self.all_variants.items():
            base_ports = self.piece_ports_base.get(p_id, {})
            for v in variants:
                rot_count = 0
                if "_Rot" in v.variant_id:
                    rot_deg = int(v.variant_id.split("_Rot")[1])
                    rot_count = rot_deg // 90
                
                rotated_ports = {}
                for coord, ports in base_ports.items():
                    curr_c = coord
                    curr_p = ports
                    for _ in range(rot_count):
                        curr_c = self.factory.rotate_coord(curr_c)
                        curr_p = {self.factory.rotate_dir(d) for d in curr_p}
                    rotated_ports[curr_c] = curr_p
                self.variant_ports[v.variant_id] = rotated_ports

                if p_id == "YellowSeesaw":
                    c = (0,0)
                    d = Direction.LEFT
                    for _ in range(rot_count):
                        c = self.factory.rotate_coord(c)
                        d = self.factory.rotate_dir(d)
                    self.yellow_entries[v.variant_id] = (c[0], c[1], d)

    def solve(self, initial_board, remaining_piece_ids, verbose=False):
        self.verbose = verbose
        self.visited_count = 0
        self.next_print_n = 1

        dog_pos = None
        trainer_pos = None
        for p_id, (v, rx, ry) in initial_board.placed_pieces.items():
            if p_id == "Dog": dog_pos = (rx, ry)
            elif p_id == "Trainer": trainer_pos = (rx, ry)
        
        if not dog_pos or not trainer_pos:
            return None

        # Find Dog piece and its connections
        dog_v, dog_rx, dog_ry = initial_board.placed_pieces["Dog"]
        dog_conns = self.variant_ports[dog_v.variant_id].get((dog_pos[0] - dog_rx, dog_pos[1] - dog_ry), set())
        
        result = None
        for start_dir in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            # Valid if it's a defined connection OR if it leads to an empty ground square
            is_valid_start = False
            if dog_conns:
                if start_dir in dog_conns:
                    is_valid_start = True
            else:
                # If Dog is on a piece with no connections (like the Dog piece itself),
                # we can move in any direction that is in bounds.
                # Actually, the _dfs will check bounds and piece connections of the NEXT square.
                is_valid_start = True
            
            if is_valid_start:
                # Start at GROUND level
                res = self._dfs(dog_pos, Level.GROUND, start_dir, initial_board, set(remaining_piece_ids), {(dog_pos[0], dog_pos[1], Level.GROUND)}, None, [(dog_pos[0], dog_pos[1], "Dog", start_dir)])
                if res:
                    result = res
                    break
        
        if self.verbose:
            print(f"Total states traversed: {self.visited_count}")
        return result

    def _is_path_compatible(self, variant, root_x, root_y, current_path, current_exit_dir):
        # Check if the piece we are placing at root_x, root_y is compatible 
        # with any squares already in the Dog's path.
        for i, (px, py, p_id, in_dir) in enumerate(current_path):
            dx, dy = px - root_x, py - root_y
            if (dx, dy) in variant.footprint:
                # Square was traversed. Must allow in_dir and out_dir.
                out_dir = current_path[i+1][3] if i < len(current_path) - 1 else current_exit_dir
                
                conns = self.variant_ports[variant.variant_id].get((dx, dy), set())
                if in_dir.reverse() not in conns or out_dir not in conns:
                    return False
        return True

    def _get_piece_at(self, board, x, y, level):
        p_id = board.get_occupant(x, y, level)
        if p_id:
            # Handle shared GROUND square: if level is GROUND and there's a bridge,
            # we should check if there's another piece here (the tunnel).
            if level == Level.GROUND:
                v, rx, ry = board.placed_pieces[p_id]
                if v.is_bridge:
                    # Look for other pieces that are NOT the bridge
                    for other_id, (ov, orx, ory) in board.placed_pieces.items():
                        if other_id == p_id: continue
                        # We don't check for ov.is_bridge because only one bridge exists
                        for odx, ody in ov.footprint:
                            if orx + odx == x and ory + ody == y:
                                return ov, x - orx, y - ory
                    
                    # If no other piece, return the bridge itself (as a GROUND occupant)
                    return v, x - rx, y - ry
            
            v, rx, ry = board.placed_pieces[p_id]
            return v, x - rx, y - ry
        return None, 0, 0

    def _dfs(self, curr_pos, curr_level, incoming_dir, board, remaining_piece_ids, visited, prev_piece_id, current_path):
        self.visited_count += 1
        if self.verbose and self.visited_count == self.next_print_n:
            from visualizer import BoardVisualizer
            print(f"--- State {self.visited_count} --- current pos {curr_pos}, current path {current_path}")
            print(BoardVisualizer.render(board))
            self.next_print_n = math.ceil(self.next_print_n * self.print_factor)
            if self.next_print_n <= self.visited_count:
                self.next_print_n = self.visited_count + 1

        x, y = curr_pos
        piece_v, dx, dy = self._get_piece_at(board, x, y, curr_level)
        
        if piece_v:
            # Yellow Seesaw 1-direction check
            if piece_v.piece_id == "YellowSeesaw" and prev_piece_id != "YellowSeesaw":
                entry_dx, entry_dy, req_back = self.yellow_entries[piece_v.variant_id]
                back_dir = incoming_dir.reverse()
                if (dx, dy) != (entry_dx, entry_dy) or back_dir != req_back:
                    return None

            conns = self.variant_ports[piece_v.variant_id].get((dx, dy), set())
            if piece_v.piece_id == "Dog":
                # Dog piece is just a marker, path continues in incoming_dir.
                # BUT if it's the very first step, incoming_dir was one of the 4 start_dirs.
                exit_dir = incoming_dir
            else:
                back_dir = incoming_dir.reverse()
                if back_dir not in conns:
                    return None
                other_conns = conns - {back_dir}
                if not other_conns:
                    return None
                exit_dir = list(other_conns)[0]
            curr_piece_id = piece_v.piece_id
        else:
            # Empty square: MUST go straight
            exit_dir = incoming_dir
            curr_piece_id = None

        next_x, next_y = x + exit_dir.dx, y + exit_dir.dy
        next_pos_2d = (next_x, next_y)
        
        if not board.is_in_bounds(next_x, next_y):
            return None

        # Try possible next levels
        for next_level in [Level.GROUND, Level.BRIDGE]:
            if (next_x, next_y, next_level) in visited:
                continue
            
            # Transition level if the CURRENT piece allows it at the NEXT square
            # Bridge pieces allow switching between GROUND and BRIDGE at legs.
            
            # 1. Check for Trainer (always GROUND)
            trainer_piece_v, t_dx, t_dy = self._get_piece_at(board, next_x, next_y, Level.GROUND)
            if trainer_piece_v and trainer_piece_v.piece_id == "Trainer":
                if next_level == Level.GROUND:
                    if not remaining_piece_ids:
                        if self._all_piece_squares_visited(board, visited | {(next_x, next_y, Level.GROUND)}):
                            return board, current_path + [(next_x, next_y, "Trainer")]
                continue # Cannot pass through Trainer or visit it early

            # 2. Check for existing piece
            next_piece_v, n_dx, n_dy = self._get_piece_at(board, next_x, next_y, next_level)
            if next_piece_v:
                conns = self.variant_ports[next_piece_v.variant_id].get((n_dx, n_dy), set())
                # If we are coming from Dog, we don't check reverse connection because Dog is just a start point.
                # Actually, the NEXT piece MUST have a port facing the Dog.
                if exit_dir.reverse() in conns:
                    res = self._dfs(next_pos_2d, next_level, exit_dir, board, remaining_piece_ids, 
                                   visited | {(next_x, next_y, next_level)}, curr_piece_id, 
                                   current_path + [(next_x, next_y, next_piece_v.piece_id, exit_dir)])
                    if res: return res
            else:
                # 3. Square is empty on this level. Try placing remaining pieces.
                for p_id in list(remaining_piece_ids):
                    for v in self.all_variants[p_id]:
                        target_level = Level.BRIDGE if v.is_bridge else Level.GROUND
                        if target_level != next_level:
                            continue
                        
                        for (v_dx, v_dy) in v.footprint:
                            root_x, root_y = next_x - v_dx, next_y - v_dy
                            if board.can_place(v, root_x, root_y):
                                # Check compatibility with previous path squares covered by this piece
                                if not self._is_path_compatible(v, root_x, root_y, current_path, exit_dir):
                                    continue

                                conns = self.variant_ports[v.variant_id].get((v_dx, v_dy), set())
                                if exit_dir.reverse() in conns:
                                    board.place(v, root_x, root_y)
                                    res = self._dfs(next_pos_2d, next_level, exit_dir, board, 
                                                   remaining_piece_ids - {p_id}, 
                                                   visited | {(next_x, next_y, next_level)}, 
                                                   curr_piece_id, current_path + [(next_x, next_y, p_id, exit_dir)])
                                    if res: return res
                                    board.remove(p_id)
                
                # 4. Try moving through truly empty square (only on GROUND)
                if next_level == Level.GROUND and not board.get_occupant(next_x, next_y, Level.GROUND):
                    # Rules: "On Empty Squares, the path MUST go straight." (exit_dir == incoming_dir)
                    # IMPORTANT: Empty squares can be crossed multiple times. 
                    # We don't add them to visited to allow crossings, 
                    # but we are safe from infinite loops because turns require pieces which are in visited.
                    res = self._dfs(next_pos_2d, Level.GROUND, exit_dir, board, remaining_piece_ids, 
                                   visited, curr_piece_id, 
                                   current_path + [(next_x, next_y, None, exit_dir)])
                    if res: return res
        return None

    def _all_piece_squares_visited(self, board, visited):
        for p_id, (v, rx, ry) in board.placed_pieces.items():
            if p_id in ["Dog", "Trainer"]: continue
            # Bridges are on Level 1, others on Level 0
            level = Level.BRIDGE if v.is_bridge else Level.GROUND
            for dx, dy in v.footprint:
                conns = self.variant_ports[v.variant_id].get((dx, dy), set())
                if conns: # Only require visiting navigable squares
                    if (rx + dx, ry + dy, level) not in visited:
                        return False
        return True
