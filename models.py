from enum import Enum
from typing import List, Tuple, Dict, Optional, Set

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def dx(self):
        return self.value[0]

    @property
    def dy(self):
        return self.value[1]

    def reverse(self):
        return Direction((-self.dx, -self.dy))

class Level(Enum):
    GROUND = 0
    BRIDGE = 1

class PieceVariant:
    """
    Represents a specific orientation and configuration of a puzzle piece.
    
    Attributes:
        piece_id: The unique identifier (e.g., 'OrangeTube').
        variant_id: Unique string for this orientation (e.g., 'OrangeTube_Rot90').
        footprint: Set of relative (dx, dy) coordinates occupied.
        routing: Maps (entry_dx, entry_dy, entry_dir) -> (list of (dx, dy, level), exit_dir).
                 The list includes all squares traversed, in order.
        tunnel_compatible: Set of (dx, dy) that can be placed Level 0 under a bridge.
        is_bridge: If True, the piece's corner is on Level 1 and its legs allow Level 0 tunnels.
    """
    def __init__(self, piece_id: str, variant_id: str, 
                 footprint: Set[Tuple[int, int]], 
                 routing: Dict[Tuple[Tuple[int, int], Direction], Tuple[List[Tuple[int, int, Level]], Direction]],
                 tunnel_compatible: Set[Tuple[int, int]] = None,
                 bridge_legs: Set[Tuple[int, int]] = None,
                 is_bridge: bool = False):
        self.piece_id = piece_id
        self.variant_id = variant_id
        self.footprint = footprint
        self.routing = routing
        self.tunnel_compatible = tunnel_compatible or set()
        self.bridge_legs = bridge_legs or set()
        self.is_bridge = is_bridge
        self.char_map = {} # To be injected by factory

    def routing_info_at(self, dx: int, dy: int) -> Set[Direction]:
        """Returns the directions the path connects to at relative square (dx, dy)."""
        connections = set()
        for (start_coord, entry_dir), (path, exit_dir) in self.routing.items():
            # Check if this square is on the path
            for i in range(len(path)):
                p_dx, p_dy, _ = path[i]
                if (p_dx, p_dy) == (dx, dy):
                    # Connection from entry
                    if i == 0:
                        connections.add(entry_dir.reverse())
                    else:
                        prev_dx, prev_dy, _ = path[i-1]
                        if prev_dy < dy: connections.add(Direction.UP)
                        elif prev_dy > dy: connections.add(Direction.DOWN)
                        elif prev_dx < dx: connections.add(Direction.LEFT)
                        elif prev_dx > dx: connections.add(Direction.RIGHT)
                    
                    # Connection to next
                    if i == len(path) - 1:
                        connections.add(exit_dir)
                    else:
                        next_dx, next_dy, _ = path[i+1]
                        if next_dy < dy: connections.add(Direction.UP)
                        elif next_dy > dy: connections.add(Direction.DOWN)
                        elif next_dx < dx: connections.add(Direction.LEFT)
                        elif next_dx > dx: connections.add(Direction.RIGHT)
        return connections

class Board:
    """
    Manages the 5x5 grid and the pieces placed upon it.
    """
    def __init__(self, size: int = 5):
        self.size = size
        # Each cell (x,y) can hold ground and bridge occupants.
        # grid[x][y] = {Level.GROUND: piece_id, Level.BRIDGE: piece_id}
        self.grid = [[{} for _ in range(size)] for _ in range(size)]
        self.placed_pieces = {} # piece_id -> (PieceVariant, root_x, root_y)
        self.place_count = 0
        self.remove_count = 0

    def is_in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def get_occupant(self, x: int, y: int, level: Level) -> Optional[str]:
        if not self.is_in_bounds(x, y):
            return None
        return self.grid[x][y].get(level)

    def can_place(self, variant: PieceVariant, root_x: int, root_y: int) -> bool:
        """
        Validates if a piece variant can be placed at the given root coordinates.
        Checks bounds and overlap, including the special bridge/tunnel rules.
        """
        for dx, dy in variant.footprint:
            x, y = root_x + dx, root_y + dy
            if not self.is_in_bounds(x, y):
                return False

            # Most pieces occupy GROUND. Only Dark Blue occupies BRIDGE.
            target_level = Level.BRIDGE if variant.is_bridge else Level.GROUND
            
            # Check for direct collision on the same level
            if self.get_occupant(x, y, target_level):
                return False

            # Special case: Dark Blue Bridge Leg overlaps
            if target_level == Level.GROUND:
                # If we are placing a ground piece, check if there's a bridge above
                bridge_id = self.get_occupant(x, y, Level.BRIDGE)
                if bridge_id:
                    # We can only place here if the ground piece is tunnel-compatible
                    # and the bridge piece at this spot is a 'leg'
                    if (dx, dy) not in variant.tunnel_compatible:
                        return False
                    
                    b_var, b_rx, b_ry = self.placed_pieces[bridge_id]
                    b_dx, b_dy = x - b_rx, y - b_ry
                    if (b_dx, b_dy) not in b_var.bridge_legs:
                        return False

            # Special case: Placing the Bridge itself
            if target_level == Level.BRIDGE:
                # Check what's on the GROUND at this spot
                ground_id = self.get_occupant(x, y, Level.GROUND)
                if ground_id:
                    # Corner of bridge cannot have anything under it.
                    if (dx, dy) not in variant.bridge_legs:
                        return False
                    
                    # Legs can have tunnel-compatible pieces under them.
                    g_var, g_rx, g_ry = self.placed_pieces[ground_id]
                    g_dx, g_dy = x - g_rx, y - g_ry
                    if (g_dx, g_dy) not in g_var.tunnel_compatible:
                        return False

        return True

    def place(self, variant: PieceVariant, root_x: int, root_y: int):
        """Places a piece and updates the grid state."""
        self.place_count+=1
        for dx, dy in variant.footprint:
            x, y = root_x + dx, root_y + dy
            # Dark Blue logic: Corner is Level 1, Legs are Level 1.
            # However, for simplicity, we treat the whole Bridge piece as Level 1
            # and verify GROUND compatibility in can_place.
            level = Level.BRIDGE if variant.is_bridge else Level.GROUND
            self.grid[x][y][level] = variant.piece_id
        
        self.placed_pieces[variant.piece_id] = (variant, root_x, root_y)

    def remove(self, piece_id: str):
        """Removes a piece and clears its grid entries."""
        if piece_id not in self.placed_pieces:
            return
        self.remove_count+=1
        variant, root_x, root_y = self.placed_pieces.pop(piece_id)
        for dx, dy in variant.footprint:
            x, y = root_x + dx, root_y + dy
            level = Level.BRIDGE if variant.is_bridge else Level.GROUND
            if level in self.grid[x][y]:
                del self.grid[x][y][level]
