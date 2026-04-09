# Smart Dog Solver

This is an automated solver for the **"Smart Dog"** sequential placement puzzle by **SmartGames**.

## The Game
The goal of the puzzle is to place all the available agility obstacles on the board to create a continuous path for the dog to reach the trainer.

### Core Rules:
1. **Fixed Starting Point**: The Dog and Trainer are placed according to the challenge.
2. **Obstacle Placement**: You must place all remaining obstacles (Tubes, Bridges, Hurdles, and Seesaws) onto the 5x5 grid.
3. **Valid Pathing**: The dog must be able to travel from its starting position to the trainer by following the paths built into each obstacle.
4. **Specific Obstacle Rules**:
    - **Tubes & Hurdles**: Have specific entry and exit points.
    - **Blue Bridge**: Allows the dog to cross over other obstacles.
    - **Yellow Seesaw**: Can only be entered from one specific side.
    - **Empty Squares**: If the dog crosses an empty square, it must move in a straight line.
5. **Goal**: Create a single, valid path that uses every piece provided in the challenge.

## Input Format
Challenges are stored as ASCII text files in the `questions/` directory.

### Example (`questions/1.txt`):
- `D`: Represents the Dog (Start).
- `T`: Represents the Trainer (End).
- `O`, `R`, `B`, `L`, `P`, `Y`: Represent different obstacles (Orange Tube, Red Tube, Blue Bridge, etc.).
- `-` and `|`: Represent internal paths within an obstacle.
- `=`: Represents a path on a Bridge crossing over another piece.

```text
+---+---+---+---+---+
| D |   |   |   |   |
+---+---+---+---+---+
|   | B-|-B-|-B |   |
|   | | |   | | |   |
+---+---+---+---+---+
|   |   |   |   | O |
|   |   |   |   | | |
+---+---+---+---+---+
|   | R |   | O-|-O |
|   | | |   |   |   |
+---+---+---+---+---+
|   | R |   |   | T |
+---+---+---+---+---+
```

## Usage

### Solve a Challenge
To find the valid placement and path for a specific puzzle:
```bash
python3 solver_main.py 1
```

### Sample Solver Output (Level 1)
```text
--- Parsing Puzzle 1 ---
Fixed pieces: ['Dog', 'BlueBridge', 'OrangeTube', 'RedTube', 'Trainer']
Pieces to place: ['LightBlueHurdle', 'PurpleHurdle', 'YellowSeesaw']
--- Solving ---
--- Solution Found ---
     0   1   2   3   4
   +---+---+---+---+---+
   |   |   |   |   |   |
 0 | D |   |-Y-|-Y-|-Y |
   |   |   |   |   | | |
   +---+---+---+---+---+
   |   |   |   |   |   |
 1 |   | B-|-B-|-B |   |
   |   | | |   | | |   |
   +---+---+---+---+---+
   |   | | |   |   | | |
 2 | L | L | L |   | O |
   |   | | |   |   | | |
   +---+---+---+---+---+
   |   | | |   | | | | |
 3 |   | R |   | O-|-O |
   |   | | |   |   |   |
   +---+---+---+---+---+
   |   | | |   |   |   |
 4 |   | R-|-P-|-P-| T |
   |   |   |   |   |   |
   +---+---+---+---+---+

--- Obstacle Moving Order ---
Dog -> YellowSeesaw -> OrangeTube -> BlueBridge -> LightBlueHurdle -> RedTube -> PurpleHurdle -> Trainer
```

## Implementation Details
- **DFS Solver**: Uses Depth-First Search with backtracking to explore valid piece placements and path combinations.
- **3D Logic**: Handles overlapping pieces using a two-layer grid system (`GROUND` and `BRIDGE`).
- **Dynamic Rotation**: Automatically tests all 4 rotations for every obstacle being placed.
- **Path Validation**: Ensures the dog's path is continuous and adheres to piece-specific directional constraints (like the Seesaw's one-way entry).
