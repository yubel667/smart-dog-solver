from models import Board, Direction, Level, PieceVariant
from factory import PieceFactory

class Solver:
    def __init__(self):
        self.factory = PieceFactory()
        self.all_variants = self.factory.get_all_piece_variants()
        
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

    def solve(self, initial_board, remaining_piece_ids):
        dog_pos = None
        trainer_pos = None
        for p_id, (v, rx, ry) in initial_board.placed_pieces.items():
            if p_id == "Dog": dog_pos = (rx, ry)
            elif p_id == "Trainer": trainer_pos = (rx, ry)
        
        if not dog_pos or not trainer_pos:
            return None

        for start_dir in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            # Start at GROUND level
            res = self._dfs(dog_pos, Level.GROUND, start_dir, initial_board, set(remaining_piece_ids), {(dog_pos[0], dog_pos[1], Level.GROUND)}, None, [(dog_pos[0], dog_pos[1], "Dog")])
            if res: return res
        return None

    def _get_piece_at(self, board, x, y, level):
        p_id = board.get_occupant(x, y, level)
        if p_id:
            v, rx, ry = board.placed_pieces[p_id]
            return v, x - rx, y - ry
        return None, 0, 0

    def _dfs(self, curr_pos, curr_level, incoming_dir, board, remaining_piece_ids, visited, prev_piece_id, current_path):
        # print(f"DEBUG: at {curr_pos} {curr_level} incoming {incoming_dir} remaining {remaining_piece_ids}")
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
            exit_dir = incoming_dir
            curr_piece_id = None

        next_x, next_y = x + exit_dir.dx, y + exit_dir.dy
        next_pos_2d = (next_x, next_y)
        
        if not board.is_in_bounds(next_x, next_y):
            return None

        # Check for Trainer (always GROUND)
        if board.get_occupant(next_x, next_y, Level.GROUND) == "Trainer":
            final_path = current_path + [(next_x, next_y, "Trainer")]
            if not remaining_piece_ids:
                if self._all_piece_squares_visited(board, visited | {(next_x, next_y, Level.GROUND)}):
                    return board, final_path
            return None

        # Try possible next levels
        for next_level in [Level.GROUND, Level.BRIDGE]:
            if (next_x, next_y, next_level) in visited:
                continue
                
            next_piece_v, n_dx, n_dy = self._get_piece_at(board, next_x, next_y, next_level)
            if next_piece_v:
                conns = self.variant_ports[next_piece_v.variant_id].get((n_dx, n_dy), set())
                if exit_dir.reverse() in conns:
                    res = self._dfs(next_pos_2d, next_level, exit_dir, board, remaining_piece_ids, visited | {(next_x, next_y, next_level)}, curr_piece_id, current_path + [(next_x, next_y, next_piece_v.piece_id)])
                    if res: return res
            else:
                # Potential empty square or piece placement (only on GROUND)
                if next_level == Level.GROUND and not board.get_occupant(next_x, next_y, Level.BRIDGE):
                    if not remaining_piece_ids:
                        res = self._dfs(next_pos_2d, Level.GROUND, exit_dir, board, remaining_piece_ids, visited | {(next_x, next_y, Level.GROUND)}, curr_piece_id, current_path + [(next_x, next_y, None)])
                        if res: return res
                    else:
                        # Try placing remaining pieces
                        for p_id in list(remaining_piece_ids):
                            for v in self.all_variants[p_id]:
                                target_level = Level.BRIDGE if v.is_bridge else Level.GROUND
                                # Only place on the level we are currently checking
                                if target_level != next_level: continue
                                
                                for (v_dx, v_dy) in v.footprint:
                                    root_x, root_y = next_x - v_dx, next_y - v_dy
                                    if board.can_place(v, root_x, root_y):
                                        conns = self.variant_ports[v.variant_id].get((v_dx, v_dy), set())
                                        if exit_dir.reverse() in conns:
                                            board.place(v, root_x, root_y)
                                            res = self._dfs(next_pos_2d, next_level, exit_dir, board, remaining_piece_ids - {p_id}, visited | {(next_x, next_y, next_level)}, curr_piece_id, current_path + [(next_x, next_y, p_id)])
                                            if res: return res
                                            board.remove(p_id)
                        # Also try passing through empty square if allowed
                        res = self._dfs(next_pos_2d, Level.GROUND, exit_dir, board, remaining_piece_ids, visited | {(next_x, next_y, Level.GROUND)}, curr_piece_id, current_path + [(next_x, next_y, None)])
                        if res: return res
        return None

    def _all_piece_squares_visited(self, board, visited):
        for p_id, (v, rx, ry) in board.placed_pieces.items():
            if p_id in ["Dog", "Trainer"]: continue
            level = Level.BRIDGE if v.is_bridge else Level.GROUND
            for dx, dy in v.footprint:
                conns = self.variant_ports[v.variant_id].get((dx, dy), set())
                if conns: # Only require visiting navigable squares
                    if (rx + dx, ry + dy, level) not in visited:
                        return False
        return True
