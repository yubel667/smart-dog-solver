from models import Board, Direction, Level, PieceVariant
from factory import PieceFactory

class Solver:
    def __init__(self):
        self.factory = PieceFactory()
        self.all_variants = self.factory.get_all_piece_variants()
        self.variant_ports = {}
        for p_id, variants in self.all_variants.items():
            for v in variants:
                conn_map = {}
                for dx, dy in v.footprint:
                    conn_map[(dx, dy)] = v.routing_info_at(dx, dy)
                self.variant_ports[v.variant_id] = conn_map

    def solve(self, initial_board, remaining_piece_ids):
        dog_pos = None
        trainer_pos = None
        for p_id, (v, rx, ry) in initial_board.placed_pieces.items():
            if p_id == "Dog": dog_pos = (rx, ry)
            elif p_id == "Trainer": trainer_pos = (rx, ry)
        if not dog_pos or not trainer_pos: return None
        for start_dir in [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]:
            res = self._dfs(dog_pos, start_dir, initial_board, set(remaining_piece_ids), {dog_pos})
            if res: return res
        return None

    def _get_piece_at(self, board, x, y):
        for p_id, (v, rx, ry) in board.placed_pieces.items():
            dx, dy = x - rx, y - ry
            if (dx, dy) in v.footprint:
                # Prioritize Ground pieces for now
                if not v.is_bridge and board.grid[x][y].get(Level.GROUND) == p_id:
                    return v, dx, dy
                if v.is_bridge and board.grid[x][y].get(Level.BRIDGE) == p_id:
                    return v, dx, dy
        return None, 0, 0

    def _dfs(self, curr_pos, incoming_dir, board, remaining_piece_ids, visited):
        x, y = curr_pos
        piece_v, dx, dy = self._get_piece_at(board, x, y)
        if piece_v:
            conns = self.variant_ports[piece_v.variant_id][(dx, dy)]
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
        else:
            exit_dir = incoming_dir

        next_x, next_y = x + exit_dir.dx, y + exit_dir.dy
        next_pos = (next_x, next_y)
        if not board.is_in_bounds(next_x, next_y): return None
        if board.get_occupant(next_x, next_y, Level.GROUND) == "Trainer":
            if not remaining_piece_ids and self._all_piece_squares_visited(board, visited | {next_pos}):
                return board
            return None
        if next_pos in visited: return None

        next_piece_v, _, _ = self._get_piece_at(board, next_x, next_y)
        if next_piece_v:
            return self._dfs(next_pos, exit_dir, board, remaining_piece_ids, visited | {next_pos})
        else:
            for p_id in list(remaining_piece_ids):
                for v in self.all_variants[p_id]:
                    for (v_dx, v_dy) in v.footprint:
                        root_x, root_y = next_x - v_dx, next_y - v_dy
                        if board.can_place(v, root_x, root_y):
                            conns = self.variant_ports[v.variant_id][(v_dx, v_dy)]
                            if exit_dir.reverse() in conns:
                                board.place(v, root_x, root_y)
                                res = self._dfs(next_pos, exit_dir, board, remaining_piece_ids - {p_id}, visited | {next_pos})
                                if res: return res
                                board.remove(p_id)
            return self._dfs(next_pos, exit_dir, board, remaining_piece_ids, visited | {next_pos})

    def _all_piece_squares_visited(self, board, visited):
        for p_id, (v, rx, ry) in board.placed_pieces.items():
            for dx, dy in v.footprint:
                if (rx + dx, ry + dy) not in visited:
                    return False
        return True
