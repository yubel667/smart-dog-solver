from typing import List, Tuple, Set, Dict
from models import PieceVariant, Direction, Level

class PieceFactory:
    @staticmethod
    def rotate_coord(coord: Tuple[int, int]) -> Tuple[int, int]:
        return (-coord[1], coord[0])

    @staticmethod
    def rotate_dir(d: Direction) -> Direction:
        rot_map = {
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP
        }
        return rot_map[d]

    @classmethod
    def generate_rotations(cls, piece_id: str, 
                           base_footprint: Set[Tuple[int, int]], 
                           base_routing: Dict,
                           is_bridge: bool = False,
                           prefix: str = "") -> List[PieceVariant]:
        variants = []
        curr_footprint = base_footprint
        curr_routing = base_routing

        for i in range(4):
            v_id = f"{piece_id}{prefix}_Rot{i*90}"
            variant = PieceVariant(piece_id=piece_id, variant_id=v_id,
                                   footprint=curr_footprint, routing=curr_routing,
                                   is_bridge=is_bridge)
            variants.append(variant)
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
        # Base: (0,0) corner, (1,0) leg1, (0,1) leg2
        footprint = {(0,0), (1,0), (0,1)}
        routing = {
            # (0,0): connects UP and DOWN
            ((0,0), Direction.LEFT): ([(0,0, Level.GROUND)], Direction.RIGHT),
            # (1,0): connects UP and LEFT
            ((1,0), Direction.LEFT): ([(1,0, Level.GROUND)], Direction.UP),
            # (0,1): connects UP and RIGHT
            ((0,1), Direction.LEFT): ([(0,1, Level.GROUND)], Direction.DOWN)
        }
        return cls.generate_rotations("OrangeTube", footprint, routing)

    @classmethod
    def create_red_tube(cls) -> List[PieceVariant]:
        footprint = {(0,0), (1,0)}
        routing = {
            ((0,0), Direction.LEFT): ([(0,0, Level.GROUND)], Direction.RIGHT),
            ((1,0), Direction.LEFT): ([(1,0, Level.GROUND)], Direction.DOWN)
        }
        return cls.generate_rotations("RedTube", footprint, routing)

    @classmethod
    def create_blue_bridge(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1), (0,2)}
        routing = {
            ((0,0), Direction.DOWN): ([(0,0, Level.BRIDGE)], Direction.RIGHT),
            ((0,0), Direction.RIGHT): ([(0,0, Level.GROUND)], Direction.RIGHT),
            ((0,1), Direction.UP): ([(0,1, Level.BRIDGE)], Direction.DOWN),
            ((0,2), Direction.UP): ([(0,2, Level.BRIDGE)], Direction.RIGHT),
            ((0,2), Direction.RIGHT): ([(0,2, Level.GROUND)], Direction.RIGHT)
        }
        return cls.generate_rotations("BlueBridge", footprint, routing, is_bridge=True)

    @classmethod
    def create_light_blue_hurdle(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1), (0,2)}
        routing = {
            ((0,0), Direction.UP): ([(0,0, Level.GROUND)], Direction.DOWN),
            ((0,1), Direction.UP): ([(0,1, Level.GROUND)], Direction.DOWN),
            ((0,2), Direction.UP): ([(0,2, Level.GROUND)], Direction.DOWN)
        }
        return cls.generate_rotations("LightBlueHurdle", footprint, routing)

    @classmethod
    def create_purple_hurdle(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1)}
        routing = {
            ((0,0), Direction.UP): ([(0,0, Level.GROUND)], Direction.DOWN),
            ((0,1), Direction.UP): ([(0,1, Level.GROUND)], Direction.DOWN)
        }
        return cls.generate_rotations("PurpleHurdle", footprint, routing)

    @classmethod
    def create_yellow_seesaw(cls) -> List[PieceVariant]:
        footprint = {(0,0), (0,1), (0,2)}
        routing = {
            ((0,0), Direction.UP): ([(0,0, Level.GROUND)], Direction.DOWN),
            ((0,1), Direction.UP): ([(0,1, Level.GROUND)], Direction.DOWN),
            ((0,2), Direction.UP): ([(0,2, Level.GROUND)], Direction.RIGHT)
        }
        return cls.generate_rotations("YellowSeesaw", footprint, routing)

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
