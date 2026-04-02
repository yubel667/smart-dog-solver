# Smart Dog Solver Ruleset

This document provides a fully self-contained, formal specification of the "Smart Dog" puzzle game by SmartGames, designed specifically to be implemented as a programmatic solver. All ambiguities from the manual have been resolved into precise geometric and logical constraints.

## 1. Grid and Objective
- **Grid:** 5x5 squares. Coordinates `(x, y)` from `(0,0)` to `(4,4)`.
- **Objective:** Create a single continuous, non-branching path from the **Dog** to the **Trainer** using every obstacle exactly once.
- **Completion:** Every square of every placed obstacle MUST be traversed by the path exactly once. The only exception is squares under the Dark Blue bridge, which are traversed twice (once over the bridge, once through the tunnel).

## 2. Obstacles and Footprints
There are 6 obstacles, plus the Dog and Trainer. Pieces cannot be placed outside the 5x5 grid. Pieces cannot overlap, EXCEPT for specific "tunnel" pieces placed under the legs of the Dark Blue Bridge.

| ID | Name | Color | Footprint Shape | Size | Allowed Orientations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A** | Dog | Yellowish | 1x1 Square | 1 sq | 1 (Start point) |
| **B** | Trainer | Red | 1x1 Square | 1 sq | 1 (End point) |
| **C** | Orange Tube | Orange | L-shape | 3 sq | 4 rotations |
| **D** | Dark Blue Bridge | Dark Blue | L-shape | 3 sq | 4 rotations |
| **E** | Light Blue Hurdle | Light Blue | 1x3 Straight | 3 sq | 2 rotations |
| **F** | Purple Hurdle | Purple | 1x2 Straight | 2 sq | 2 rotations |
| **G** | Yellow Seesaw | Yellow | 1x3 Straight | 3 sq | 8 (4 rot x 2 chiral)* |
| **H** | Red Tube | Red | L-shape | 3 sq | 4 rotations |

*\*Note on Yellow Seesaw: The physical piece forces entry at one end and turns 90° at the other. To account for chiral ambiguity in the manual's 2D diagrams, the solver should evaluate both left-turning and right-turning variants of this piece (8 total orientations).*

### Obstacle Track Properties:
- **L-Shape Curves (C, H, D):** Consist of a `Corner` square and two `Leg` squares.
  - **C & H (Tubes):** Path enters one Leg, turns 90° at the Corner, and exits the other Leg.
  - **D (Bridge):** Path enters one Leg (ramp up), turns 90° at the Corner, and exits the other Leg (ramp down). This path is strictly on "Level 1".
- **Straight Hurdles (E, F):**
  - Path goes straight through all squares along the piece's long axis.
- **Yellow Seesaw (G):**
  - Consists of an `Entry` square, a `Middle` square, and an `Exit` square arranged in a 1x3 line.
  - Path MUST enter at the `Entry` square (the low end with the arrow), go straight through the `Middle` square, and turn 90° to exit out the side of the `Exit` square.

## 3. The Bridge / Tunnel Mechanics
The Dark Blue Bridge (D) is the ONLY piece that allows board squares to be shared.
- The **Corner** of the Dark Blue bridge CANNOT be shared.
- The two **Legs** of the Dark Blue bridge CAN be shared with specific parts of other pieces, creating a "Tunnel" (Level 0) under the "Bridge" (Level 1).
- **Tunnel Compatibility:**
  - **Allowed:** The `Leg` squares of Orange (C) and Red (H), and the two `End` squares of Light Blue (E).
  - **Forbidden:** The `Corner` squares of Orange (C) and Red (H), the `Middle` square of Light Blue (E), and ANY part of Purple (F) or Yellow (G).
- **Orthogonal Crossing:** When a square is shared, the Tunnel path (Level 0) MUST cross orthogonally to the Bridge path (Level 1) above it. (e.g., if the Dark Blue leg connects to its corner along the Y-axis, the tunnel path underneath it must run along the X-axis).

## 4. Path and Movement Constraints
- **Start/End:** The path starts at the Dog (A) in any of the 4 cardinal directions. It ends at the Trainer (B) arriving from any direction.
- **Movement:** Only orthogonal movement (Up, Down, Left, Right). No diagonals.
- **Inertia:** 
  - On **Empty Squares**, the path MUST go straight. It cannot turn.
  - On **Straight pieces (E, F)** and the straight parts of Yellow (G), the path MUST go straight.
  - The path CANNOT cross an empty square twice. (The only allowed self-intersection is at the Bridge overlaps).
- **Turning:** The path ONLY turns 90° when forced by the track of a curved piece:
  - The Corner of Orange (C), Red (H), Dark Blue (D).
  - The Exit square of Yellow (G).
- **Adherence:** The path must strictly follow the entry/exit directions dictated by the pieces. A straight section of a piece cannot be entered from its side.

## 5. Solver State and Rules
A valid solution must satisfy:
1.  **Placement:** Dog and Trainer are at their fixed starting positions. All 6 obstacles (C, D, E, F, G, H) are placed on the 5x5 grid without overlapping (except valid bridge/tunnel overlaps). Any pre-fixed obstacles in the challenge are in their required positions/orientations.
2.  **Path Traversal:** A single continuous path connects the Dog to the Trainer.
3.  **Completeness:** Every square occupied by an obstacle is traversed exactly once by the path. (Shared bridge leg squares are traversed twice: once on Level 1, once on Level 0).
4.  **Directionality:** The path strictly obeys the inertia rules and the mandatory entry requirement of the Yellow Seesaw.