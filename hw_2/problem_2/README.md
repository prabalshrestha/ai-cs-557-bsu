# Problem 2 Solution: Search Algorithms on 10x10 Maze

## Overview

This solution implements and compares 5 search algorithms on a 10x10 grid maze as specified in HW2 Problem 2.

## Implementation Details

### Maze Configuration

- **Grid Size**: 10x10 (rows r0-r9, columns c0-c9)
- **Start Position**: (0, 0) - top-left corner
- **Goal Position**: (9, 9) - bottom-right corner
- **Obstacles (#)**: Impassable cells at specified coordinates
- **High-cost cells (|)**: Cost = 100 at specified coordinates
- **Normal cells (.)**: Cost = 1

### Search Algorithms Implemented

1. **Depth-First Search (DFS)**

   - Uses stack (LIFO) for frontier
   - Explores deepest paths first

2. **Breadth-First Search (BFS)**

   - Uses queue (FIFO) for frontier
   - Explores shallowest paths first

3. **Uniform Cost Search (UCS)**

   - Uses priority queue ordered by path cost
   - Guarantees optimal solution

4. **Greedy Best-First Search**

   - Uses Manhattan distance heuristic: h(x) = |r(x) - r(G)| + |c(x) - c(G)|
   - Prioritizes nodes closest to goal

5. **A\* Search**
   - Uses f(x) = g(x) + h(x) where g(x) is path cost and h(x) is Manhattan distance
   - Guarantees optimal solution with admissible heuristic

### Frontier Insertion Order

All algorithms follow the specified order when adding successors:

- **Top** → **Left** → **Right** → **Bottom**
- This ensures consistent behavior across all algorithms

## Performance Results

| Algorithm  | Nodes Expanded | Path Cost | Path Length | Time (ms) |
| ---------- | -------------- | --------- | ----------- | --------- |
| **BFS**    | 101            | 216       | 18          | 0.07      |
| **DFS**    | 23             | 121       | 22          | 0.03      |
| **UCS**    | 70             | 28        | 28          | 0.10      |
| **Greedy** | 21             | 216       | 18          | 0.04      |
| **A\***    | 55             | 28        | 28          | 0.08      |

## Key Findings

### Optimal Solutions

- **UCS** and **A\*** found optimal paths with cost = 28
- Both algorithms guarantee optimality when using admissible heuristics

### Efficiency Analysis

- **Fastest execution**: DFS (0.03 ms)
- **Lowest path cost**: UCS and A\* (28)
- **Fewest nodes expanded**: Greedy (21)

### Algorithm Characteristics

- **BFS**: Explores many nodes but finds reasonable path
- **DFS**: Fast execution but suboptimal path (cost = 121)
- **UCS**: Optimal solution but moderate node expansion
- **Greedy**: Most efficient node expansion but suboptimal path (cost = 216)
- **A\***: Best balance of optimality and efficiency

### Metrics Collected

1. **Nodes Expanded**: Total nodes removed from frontier and expanded
2. **Total Path Cost**: Sum of cell-entry costs along final path
3. **Total Path Length**: Number of moves in final path
4. **Execution Time**: Wall-clock time in milliseconds

### Verification

- All algorithms successfully find paths from start to goal
- Manhattan distance heuristic correctly implemented
- Frontier insertion order properly maintained
- Type safety ensured with proper annotations

## Usage

```bash
python main.py
```

The program will:

1. Display the maze layout
2. Run all 5 search algorithms
3. Display performance comparison table
4. Provide analysis of best performing algorithms
