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

    @classmethod
    def build_routing(cls, connections: Dict[Tuple[int, int], Set[Direction]], is_bridge: bool = False) -> Dict:
        """Helper to build routing from a connection map."""
        routing = {}
        for coord, dirs in connections.items():
            for d in dirs:
                # Use a dummy entry to trigger the routing_info_at logic
                # entry_dir.reverse() will result in d being returned by routing_info_at
                level = Level.BRIDGE if is_bridge else Level.GROUND
                routing[(coord, d.reverse())] = ([(coord[0], coord[1], level)], d)
        return routing

    @classmethod
    def generate_rotations(cls, piece_id: str, 
                           base_footprint: Set[Tuple[int, int]], 
                           base_routing: Dict,
                           is_bridge: bool = False,
                           prefix: str = "") -> List[PieceVariant]:
        """Generates 4 rotated variants from a base configuration."""
        variants = []
        curr_footprint = base_footprint
        curr_routing = base_routing

        for i in range(4):
            v_id = f"{piece_id}{prefix}_Rot{i*90}"
            variant = PieceVariant(
                piece_id=piece_id,
                variant_id=v_id,
                footprint=curr_footprint,
                routing=curr_routing,
                is_bridge=is_bridge
            )
            variants.append(variant)
            
            # Rotate for next iteration
            curr_footprint = {cls.rotate_coord(c) for c in curr_footprint}
            
            new_routing = {}
            for (start_coord, entry_dir), (path, exit_dir) in curr_routing.items():
                new_start = cls.rotate_coord(start_coord)
                new_entry = cls.rotate_dir(entry_dir)
                new_path = [(cls.rotate_coord((p[0], p[1]))[0], cls.rotate_coord((p[0], p[1]))[1], p[2]) for p in path]
                new_exit = cls.rotate_dir(exit_dir)
                new_routing[(new_start, new_entry)] = (new_path, new_exit)
            curr_routing = new_routing

        return variants

    @classmethod
    def create_orange_tube(cls) -> List[PieceVariant]:
        footprint = {(0,0), (1,0), (1,-1)}
        connections = {
            (0,0): {Direction.LEFT, Direction.RIGHT},
            (1,0): {Direction.UP, Direction.LEFT},
            (1,-1): {Direction.DOWN, Direction.LEFT}
        }
        return cls.generate_rotations("OrangeTube", footprint, cls.build_routing(connections))

    @classmethod
    def create_red_tube(cls) -> List[PieceVariant]:
        footprint = {(0,0), (1,0)}
        connections = {
            (0,0): {Direction.LEFT, Direction.RIGHT},
            (1,0): {Direction.DOWN, Direction.LEFT}
        }
        return cls.generate_rotations("RedTube", footprint, cls.build_routing(connections))

    @classmethod
    def create_blue_bridge(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1), (0,2)}
        connections = {
            (0,0): {Direction.DOWN, Direction.RIGHT},
            (0,1): {Direction.UP, Direction.DOWN},
            (0,2): {Direction.UP, Direction.RIGHT}
        }
        return cls.generate_rotations("BlueBridge", footprint, cls.build_routing(connections, is_bridge=True), is_bridge=True)

    @classmethod
    def create_light_blue_hurdle(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1), (0,2)}
        connections = {
            (0,0): {Direction.UP, Direction.DOWN},
            (0,1): {Direction.UP, Direction.DOWN},
            (0,2): {Direction.UP, Direction.DOWN}
        }
        return cls.generate_rotations("LightBlueHurdle", footprint, cls.build_routing(connections))

    @classmethod
    def create_purple_hurdle(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1)}
        connections = {
            (0,0): {Direction.UP, Direction.DOWN},
            (0,1): {Direction.UP, Direction.DOWN}
        }
        return cls.generate_rotations("PurpleHurdle", footprint, cls.build_routing(connections))

    @classmethod
    def create_yellow_seesaw(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1), (0,2)}
        connections = {
            (0,0): {Direction.UP, Direction.DOWN},
            (0,1): {Direction.UP, Direction.DOWN},
            (0,2): {Direction.UP, Direction.RIGHT}
        }
        return cls.generate_rotations("YellowSeesaw", footprint, cls.build_routing(connections))

    @classmethod
    def create_dog(cls) -> List[PieceVariant]:
        return [PieceVariant("Dog", "Dog", {(0,0)}, {})]

    @classmethod
    def create_trainer(cls) -> List[PieceVariant]:
        return [PieceVariant("Trainer", "Trainer", {(0,0)}, {})]

    @classmethod
    def get_all_piece_variants(cls) -> Dict[str, List[PieceVariant]]:
        return {
            "OrangeTube": cls.create_orange_tube(),
            "RedTube": cls.create_red_tube(),
            "BlueBridge": cls.create_blue_bridge(),
            "LightBlueHurdle": cls.create_light_blue_hurdle(),
            "PurpleHurdle": cls.create_purple_hurdle(),
            "YellowSeesaw": cls.create_yellow_seesaw(),
            "Dog": cls.create_dog(),
            "Trainer": cls.create_trainer()
        }
