from typing import List, Tuple, Set, Dict
from models import PieceVariant, Direction, Level

class PieceFactory:
    @staticmethod
    def rotate_coord(coord: Tuple[int, int]) -> Tuple[int, int]:
        """Rotates a coordinate (dx, dy) 90 degrees clockwise."""
        return (-coord[1], coord[0])

    @staticmethod
    def rotate_dir(d: Direction) -> Direction:
        """Rotates a direction 90 degrees clockwise."""
        rot_map = {
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP
        }
        return rot_map[d]

    @staticmethod
    def mirror_coord(coord: Tuple[int, int]) -> Tuple[int, int]:
        """Mirrors a coordinate (dx, dy) across the X-axis (flips Y)."""
        return (coord[0], -coord[1])

    @staticmethod
    def mirror_dir(d: Direction) -> Direction:
        """Mirrors a direction across the X-axis."""
        mirror_map = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.LEFT,
            Direction.RIGHT: Direction.RIGHT
        }
        return mirror_map[d]

    @classmethod
    def generate_rotations(cls, piece_id: str, 
                           base_footprint: Set[Tuple[int, int]], 
                           base_routing: Dict,
                           base_tunnel: Set[Tuple[int, int]] = None,
                           is_bridge: bool = False,
                           prefix: str = "") -> List[PieceVariant]:
        """Generates 4 rotated variants from a base configuration."""
        variants = []
        curr_footprint = base_footprint
        curr_routing = base_routing
        curr_tunnel = base_tunnel or set()

        for i in range(4):
            # Calculate connectivity for each square in the footprint
            connections = {coord: set() for coord in curr_footprint}
            for (start_coord, entry_dir), (path, exit_dir) in curr_routing.items():
                # Entry connection (path[0] is entered FROM entry_dir.reverse())
                connections[start_coord].add(entry_dir.reverse())
                
                # Internal connections
                for j in range(len(path)):
                    curr_p = (path[j][0], path[j][1])
                    if j > 0:
                        prev_p = (path[j-1][0], path[j-1][1])
                        dx, dy = curr_p[0] - prev_p[0], curr_p[1] - prev_p[1]
                        if (dx, dy) == (0, 1):
                            connections[prev_p].add(Direction.DOWN)
                            connections[curr_p].add(Direction.UP)
                        elif (dx, dy) == (0, -1):
                            connections[prev_p].add(Direction.UP)
                            connections[curr_p].add(Direction.DOWN)
                        elif (dx, dy) == (1, 0):
                            connections[prev_p].add(Direction.RIGHT)
                            connections[curr_p].add(Direction.LEFT)
                        elif (dx, dy) == (-1, 0):
                            connections[prev_p].add(Direction.LEFT)
                            connections[curr_p].add(Direction.RIGHT)
                
                # Exit connection (last square of path is exited TO exit_dir)
                last_p = (path[-1][0], path[-1][1])
                connections[last_p].add(exit_dir)
            
            # Map connections to box drawing characters
            # Single lines for ground, double lines for bridge
            char_map = {}
            for coord, dirs in connections.items():
                char_map[coord] = cls.get_box_char(dirs, is_bridge)

            v_id = f"{piece_id}{prefix}_Rot{i*90}"
            variant = PieceVariant(
                piece_id=piece_id,
                variant_id=v_id,
                footprint=curr_footprint,
                routing=curr_routing,
                tunnel_compatible=curr_tunnel,
                is_bridge=is_bridge
            )
            variant.char_map = char_map # Inject character map
            variants.append(variant)
            
            # Rotate for next iteration
            curr_footprint = {cls.rotate_coord(c) for c in curr_footprint}
            curr_tunnel = {cls.rotate_coord(c) for c in curr_tunnel}
            
            new_routing = {}
            for (start_coord, entry_dir), (path, exit_dir) in curr_routing.items():
                new_start = cls.rotate_coord(start_coord)
                new_entry = cls.rotate_dir(entry_dir)
                new_path = []
                for p_dx, p_dy, p_level in path:
                    rdx, rdy = cls.rotate_coord((p_dx, p_dy))
                    new_path.append((rdx, rdy, p_level))
                new_exit = cls.rotate_dir(exit_dir)
                new_routing[(new_start, new_entry)] = (new_path, new_exit)
            curr_routing = new_routing

        return variants

    @staticmethod
    def get_box_char(dirs: Set[Direction], is_bridge: bool) -> str:
        """Returns the appropriate box-drawing character for a set of connections."""
        # Ground (single) and bridge (double) characters
        ground_chars = {
            frozenset([Direction.UP, Direction.DOWN]): "┃",
            frozenset([Direction.LEFT, Direction.RIGHT]): "━",
            frozenset([Direction.UP, Direction.RIGHT]): "┗",
            frozenset([Direction.UP, Direction.LEFT]): "┛",
            frozenset([Direction.DOWN, Direction.RIGHT]): "┏",
            frozenset([Direction.DOWN, Direction.LEFT]): "┓",
            frozenset([Direction.UP, Direction.DOWN, Direction.LEFT]): "┫",
            frozenset([Direction.UP, Direction.DOWN, Direction.RIGHT]): "┣",
            frozenset([Direction.UP, Direction.LEFT, Direction.RIGHT]): "┻",
            frozenset([Direction.DOWN, Direction.LEFT, Direction.RIGHT]): "┳",
            frozenset([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]): "╋",
            frozenset([Direction.UP]): "╹",
            frozenset([Direction.DOWN]): "╻",
            frozenset([Direction.LEFT]): "╸",
            frozenset([Direction.RIGHT]): "╺",
        }
        bridge_chars = {
            frozenset([Direction.UP, Direction.DOWN]): "║",
            frozenset([Direction.LEFT, Direction.RIGHT]): "═",
            frozenset([Direction.UP, Direction.RIGHT]): "╚",
            frozenset([Direction.UP, Direction.LEFT]): "╝",
            frozenset([Direction.DOWN, Direction.RIGHT]): "╔",
            frozenset([Direction.DOWN, Direction.LEFT]): "╗",
            frozenset([Direction.UP, Direction.DOWN, Direction.LEFT]): "╣",
            frozenset([Direction.UP, Direction.DOWN, Direction.RIGHT]): "╠",
            frozenset([Direction.UP, Direction.LEFT, Direction.RIGHT]): "╩",
            frozenset([Direction.DOWN, Direction.LEFT, Direction.RIGHT]): "╦",
            frozenset([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]): "╬",
            frozenset([Direction.UP]): "╨",
            frozenset([Direction.DOWN]): "╥",
            frozenset([Direction.LEFT]): "╡",
            frozenset([Direction.RIGHT]): "╞",
        }
        chars = bridge_chars if is_bridge else ground_chars
        return chars.get(frozenset(dirs), "?")

    @classmethod
    def create_orange_tube(cls) -> List[PieceVariant]:
        # L-shape: (0,0) corner, (1,0) leg1, (0,1) leg2
        footprint = {(0,0), (1,0), (0,1)}
        tunnel = {(1,0), (0,1)}
        routing = {
            ((1,0), Direction.LEFT): ([(1,0, Level.GROUND), (0,0, Level.GROUND), (0,1, Level.GROUND)], Direction.DOWN),
            ((0,1), Direction.UP): ([(0,1, Level.GROUND), (0,0, Level.GROUND), (1,0, Level.GROUND)], Direction.RIGHT)
        }
        return cls.generate_rotations("OrangeTube", footprint, routing, tunnel)

    @classmethod
    def create_red_tube(cls) -> List[PieceVariant]:
        # Red Tube (H) is a 1x2 curved piece (2 squares)
        # (0,0) corner/leg, (1,0) leg
        footprint = {(0,0), (1,0)}
        tunnel = {(0,0), (1,0)}
        routing = {
            ((0,0), Direction.UP): ([(0,0, Level.GROUND), (1,0, Level.GROUND)], Direction.RIGHT),
            ((1,0), Direction.LEFT): ([(1,0, Level.GROUND), (0,0, Level.GROUND)], Direction.DOWN)
        }
        return cls.generate_rotations("RedTube", footprint, routing, tunnel)

    @classmethod
    def create_blue_bridge(cls) -> List[PieceVariant]:
        # L-shape: (0,0) corner, (1,0) leg1, (0,1) leg2
        # Bridge is all Level.BRIDGE (Level 1)
        footprint = {(0,0), (1,0), (0,1)}
        routing = {
            ((1,0), Direction.LEFT): ([(1,0, Level.BRIDGE), (0,0, Level.BRIDGE), (0,1, Level.BRIDGE)], Direction.DOWN),
            ((0,1), Direction.UP): ([(0,1, Level.BRIDGE), (0,0, Level.BRIDGE), (1,0, Level.BRIDGE)], Direction.RIGHT)
        }
        return cls.generate_rotations("BlueBridge", footprint, routing, is_bridge=True)

    @classmethod
    def create_light_blue_hurdle(cls) -> List[PieceVariant]:
        # 1x3 Straight
        footprint = {(0,0), (1,0), (2,0)}
        tunnel = {(0,0), (2,0)}
        routing = {
            ((0,0), Direction.RIGHT): ([(0,0, Level.GROUND), (1,0, Level.GROUND), (2,0, Level.GROUND)], Direction.RIGHT),
            ((2,0), Direction.LEFT): ([(2,0, Level.GROUND), (1,0, Level.GROUND), (0,0, Level.GROUND)], Direction.LEFT)
        }
        # Only 2 unique rotations, but generate_rotations handles 4 fine
        return cls.generate_rotations("LightBlueHurdle", footprint, routing, tunnel)

    @classmethod
    def create_purple_hurdle(cls) -> List[PieceVariant]:
        # 1x2 Straight, No tunnel
        footprint = {(0,0), (1,0)}
        routing = {
            ((0,0), Direction.RIGHT): ([(0,0, Level.GROUND), (1,0, Level.GROUND)], Direction.RIGHT),
            ((1,0), Direction.LEFT): ([(1,0, Level.GROUND), (0,0, Level.GROUND)], Direction.LEFT)
        }
        return cls.generate_rotations("PurpleHurdle", footprint, routing)

    @classmethod
    def create_yellow_seesaw(cls) -> List[PieceVariant]:
        # 1x3: (0,0) entry, (1,0) mid, (2,0) exit. Turns 90 deg at exit.
        # Chiral 1: Turns DOWN
        footprint = {(0,0), (1,0), (2,0)}
        routing_down = {
            ((0,0), Direction.RIGHT): ([(0,0, Level.GROUND), (1,0, Level.GROUND), (2,0, Level.GROUND)], Direction.DOWN)
        }
        vars_down = cls.generate_rotations("YellowSeesaw", footprint, routing_down, prefix="_ChiralA")
        
        # Chiral 2: Turns UP
        routing_up = {
            ((0,0), Direction.RIGHT): ([(0,0, Level.GROUND), (1,0, Level.GROUND), (2,0, Level.GROUND)], Direction.UP)
        }
        vars_up = cls.generate_rotations("YellowSeesaw", footprint, routing_up, prefix="_ChiralB")
        
        return vars_down + vars_up

    @classmethod
    def get_all_piece_variants(cls) -> Dict[str, List[PieceVariant]]:
        return {
            "OrangeTube": cls.create_orange_tube(),
            "RedTube": cls.create_red_tube(),
            "BlueBridge": cls.create_blue_bridge(),
            "LightBlueHurdle": cls.create_light_blue_hurdle(),
            "PurpleHurdle": cls.create_purple_hurdle(),
            "YellowSeesaw": cls.create_yellow_seesaw()
        }
