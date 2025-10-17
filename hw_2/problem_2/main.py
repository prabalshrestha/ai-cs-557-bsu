import heapq
import time
from collections import deque
from typing import List, Tuple, Set, Optional, Dict
import math

class Node:
    """Represents a node in the search tree"""
    def __init__(self, row: int, col: int, parent=None, g_cost=0, h_cost=0):
        self.row = row
        self.col = col
        self.parent = parent
        self.g_cost = g_cost  # actual cost from start
        self.h_cost = h_cost  # heuristic cost to goal
        self.f_cost = g_cost + h_cost  # total cost for A*
    
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
    
    def __hash__(self):
        return hash((self.row, self.col))
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost

class Maze:
    """Represents the 10x10 maze with obstacles and costs"""
    def __init__(self):
        self.rows = 10
        self.cols = 10
        self.start = (0, 0)  # (r0, c0)
        self.goal = (9, 9)  # (r9, c9)
        
        # Initialize grid with open cells (cost = 1)
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Set obstacles (impassable)
        obstacles = [
            (0, 2), (1, 1), (1, 2), (1, 6), (1, 7), (2, 4), (3, 1), (3, 4), (3, 6), (3, 8),
            (4, 1), (4, 4), (4, 6), (5, 1), (5, 6), (6, 3), (6, 4), (6, 8), (7, 1), (7, 7),
            (8, 3), (8, 5), (9, 5)
        ]
        
        # Set high-cost cells (cost = 100)
        high_cost_cells = [
            (2, 2), (2, 9), (5, 3), (5, 7), (5, 8), (7, 3), (9, 3)
        ]
        
        # Mark obstacles as -1 (impassable)
        for r, c in obstacles:
            self.grid[r][c] = -1
        
        # Mark high-cost cells
        for r, c in high_cost_cells:
            self.grid[r][c] = 100
    
    def is_valid(self, row: int, col: int) -> bool:
        """Check if a cell is valid (within bounds and not an obstacle)"""
        return (0 <= row < self.rows and 
                0 <= col < self.cols and 
                self.grid[row][col] != -1)
    
    def get_cost(self, row: int, col: int) -> float:
        """Get the cost to enter a cell"""
        if not self.is_valid(row, col):
            return float('inf')
        return self.grid[row][col]
    
    def get_neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get valid neighbors in the order: top, left, right, bottom"""
        neighbors = []
        directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]  # top, left, right, bottom
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid(new_row, new_col):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def manhattan_distance(self, row1: int, col1: int, row2: int, col2: int) -> int:
        """Calculate Manhattan distance between two points"""
        return abs(row1 - row2) + abs(col1 - col2)

class SearchAlgorithm:
    """Base class for search algorithms"""
    def __init__(self, maze: Maze):
        self.maze = maze
        self.nodes_expanded = 0
        self.path_cost = 0.0
        self.path_length = 0
        self.execution_time = 0.0
    
    def get_path(self, goal_node: Node) -> List[Tuple[int, int]]:
        """Reconstruct path from goal to start"""
        path = []
        current = goal_node
        while current:
            path.append((current.row, current.col))
            current = current.parent
        return path[::-1]
    
    def calculate_metrics(self, goal_node: Node) -> None:
        """Calculate path cost and length"""
        path = self.get_path(goal_node)
        self.path_length = len(path) - 1  # number of moves
        
        # Calculate total path cost
        self.path_cost = 0
        for i in range(len(path) - 1):
            r, c = path[i + 1]
            self.path_cost += self.maze.get_cost(r, c)

class DFS(SearchAlgorithm):
    """Depth-First Search implementation"""
    def search(self) -> Optional[List[Tuple[int, int]]]:
        start_time = time.time()
        
        start_row, start_col = self.maze.start
        goal_row, goal_col = self.maze.goal
        
        stack = [Node(start_row, start_col)]
        visited = set()
        
        while stack:
            current = stack.pop()
            self.nodes_expanded += 1
            
            if (current.row, current.col) in visited:
                continue
            
            visited.add((current.row, current.col))
            
            # Check if goal reached
            if current.row == goal_row and current.col == goal_col:
                self.execution_time = (time.time() - start_time) * 1000
                self.calculate_metrics(current)
                return self.get_path(current)
            
            # Get neighbors in order: top, left, right, bottom
            neighbors = self.maze.get_neighbors(current.row, current.col)
            for r, c in neighbors:
                if (r, c) not in visited:
                    neighbor = Node(r, c, current)
                    stack.append(neighbor)
        
        self.execution_time = (time.time() - start_time) * 1000
        return None

class BFS(SearchAlgorithm):
    """Breadth-First Search implementation"""
    def search(self) -> Optional[List[Tuple[int, int]]]:
        start_time = time.time()
        
        start_row, start_col = self.maze.start
        goal_row, goal_col = self.maze.goal
        
        queue = deque([Node(start_row, start_col)])
        visited = set()
        
        while queue:
            current = queue.popleft()
            self.nodes_expanded += 1
            
            if (current.row, current.col) in visited:
                continue
            
            visited.add((current.row, current.col))
            
            # Check if goal reached
            if current.row == goal_row and current.col == goal_col:
                self.execution_time = (time.time() - start_time) * 1000
                self.calculate_metrics(current)
                return self.get_path(current)
            
            # Get neighbors in order: top, left, right, bottom
            neighbors = self.maze.get_neighbors(current.row, current.col)
            for r, c in neighbors:
                if (r, c) not in visited:
                    neighbor = Node(r, c, current)
                    queue.append(neighbor)
        
        self.execution_time = (time.time() - start_time) * 1000
        return None

class UCS(SearchAlgorithm):
    """Uniform Cost Search implementation"""
    def search(self) -> Optional[List[Tuple[int, int]]]:
        start_time = time.time()
        
        start_row, start_col = self.maze.start
        goal_row, goal_col = self.maze.goal
        
        # Priority queue: (cost, node)
        pq = [(0.0, Node(start_row, start_col))]
        visited = set()
        costs = {(start_row, start_col): 0.0}
        
        while pq:
            current_cost, current = heapq.heappop(pq)
            self.nodes_expanded += 1
            
            if (current.row, current.col) in visited:
                continue
            
            visited.add((current.row, current.col))
            
            # Check if goal reached
            if current.row == goal_row and current.col == goal_col:
                self.execution_time = (time.time() - start_time) * 1000
                self.calculate_metrics(current)
                return self.get_path(current)
            
            # Get neighbors in order: top, left, right, bottom
            neighbors = self.maze.get_neighbors(current.row, current.col)
            for r, c in neighbors:
                if (r, c) not in visited:
                    new_cost = current_cost + self.maze.get_cost(r, c)
                    if (r, c) not in costs or new_cost < costs[(r, c)]:
                        costs[(r, c)] = new_cost
                        neighbor = Node(r, c, current, new_cost)
                        heapq.heappush(pq, (new_cost, neighbor))
        
        self.execution_time = (time.time() - start_time) * 1000
        return None

class GreedyBestFirst(SearchAlgorithm):
    """Greedy Best-First Search implementation"""
    def search(self) -> Optional[List[Tuple[int, int]]]:
        start_time = time.time()
        
        start_row, start_col = self.maze.start
        goal_row, goal_col = self.maze.goal
        
        # Calculate heuristic for start node
        h_cost = self.maze.manhattan_distance(start_row, start_col, goal_row, goal_col)
        start_node = Node(start_row, start_col, h_cost=h_cost)
        
        # Priority queue: (heuristic, node)
        pq = [(h_cost, start_node)]
        visited = set()
        
        while pq:
            _, current = heapq.heappop(pq)
            self.nodes_expanded += 1
            
            if (current.row, current.col) in visited:
                continue
            
            visited.add((current.row, current.col))
            
            # Check if goal reached
            if current.row == goal_row and current.col == goal_col:
                self.execution_time = (time.time() - start_time) * 1000
                self.calculate_metrics(current)
                return self.get_path(current)
            
            # Get neighbors in order: top, left, right, bottom
            neighbors = self.maze.get_neighbors(current.row, current.col)
            for r, c in neighbors:
                if (r, c) not in visited:
                    h_cost = self.maze.manhattan_distance(r, c, goal_row, goal_col)
                    neighbor = Node(r, c, current, h_cost=h_cost)
                    heapq.heappush(pq, (h_cost, neighbor))
        
        self.execution_time = (time.time() - start_time) * 1000
        return None

class AStar(SearchAlgorithm):
    """A* Search implementation"""
    def search(self) -> Optional[List[Tuple[int, int]]]:
        start_time = time.time()
        
        start_row, start_col = self.maze.start
        goal_row, goal_col = self.maze.goal
        
        # Calculate heuristic for start node
        h_cost = self.maze.manhattan_distance(start_row, start_col, goal_row, goal_col)
        start_node = Node(start_row, start_col, g_cost=0, h_cost=h_cost)
        
        # Priority queue: (f_cost, node)
        pq = [(start_node.f_cost, start_node)]
        visited = set()
        costs = {(start_row, start_col): 0.0}
        
        while pq:
            _, current = heapq.heappop(pq)
            self.nodes_expanded += 1
            
            if (current.row, current.col) in visited:
                continue
            
            visited.add((current.row, current.col))
            
            # Check if goal reached
            if current.row == goal_row and current.col == goal_col:
                self.execution_time = (time.time() - start_time) * 1000
                self.calculate_metrics(current)
                return self.get_path(current)
            
            # Get neighbors in order: top, left, right, bottom
            neighbors = self.maze.get_neighbors(current.row, current.col)
            for r, c in neighbors:
                if (r, c) not in visited:
                    new_g_cost = current.g_cost + self.maze.get_cost(r, c)
                    if (r, c) not in costs or new_g_cost < costs[(r, c)]:
                        costs[(r, c)] = new_g_cost
                        h_cost = self.maze.manhattan_distance(r, c, goal_row, goal_col)
                        neighbor = Node(r, c, current, g_cost=new_g_cost, h_cost=h_cost)
                        heapq.heappush(pq, (neighbor.f_cost, neighbor))
        
        self.execution_time = (time.time() - start_time) * 1000
        return None

def run_all_algorithms():
    """Run all search algorithms and collect metrics"""
    maze = Maze()
    algorithms = {
        'DFS': DFS(maze),
        'BFS': BFS(maze),
        'UCS': UCS(maze),
        'Greedy': GreedyBestFirst(maze),
        'A*': AStar(maze)
    }
    
    results = {}
    
    print("Running search algorithms on 10x10 maze...")
    print("=" * 60)
    
    for name, algorithm in algorithms.items():
        print(f"\nRunning {name}...")
        path = algorithm.search()
        
        if path:
            print(f"Path found with {len(path)} nodes")
            print(f"Path: {path[:5]}{'...' if len(path) > 5 else ''}")
        else:
            print("No path found!")
        
        results[name] = {
            'nodes_expanded': algorithm.nodes_expanded,
            'path_cost': algorithm.path_cost,
            'path_length': algorithm.path_length,
            'execution_time': algorithm.execution_time
        }
    
    return results

def print_results_table(results: Dict):
    """Print results in a formatted table"""
    print("\n" + "=" * 80)
    print("SEARCH ALGORITHM PERFORMANCE COMPARISON")
    print("=" * 80)
    
    # Header
    print(f"{'Algorithm':<12} {'Nodes Expanded':<15} {'Path Cost':<12} {'Path Length':<12} {'Time (ms)':<12}")
    print("-" * 80)
    
    # Results
    for algorithm in ['BFS', 'DFS', 'UCS', 'Greedy', 'A*']:
        if algorithm in results:
            r = results[algorithm]
            print(f"{algorithm:<12} {r['nodes_expanded']:<15} {r['path_cost']:<12} {r['path_length']:<12} {r['execution_time']:<12.2f}")
    
    print("=" * 80)

def print_maze(maze: Maze):
    """Print the maze for visualization"""
    print("\nMaze Layout:")
    print("S = Start, G = Goal, # = Obstacle, | = High-cost cell (100), . = Normal cell (1)")
    print()
    
    for r in range(maze.rows):
        row_str = ""
        for c in range(maze.cols):
            if (r, c) == maze.start:
                row_str += "S"
            elif (r, c) == maze.goal:
                row_str += "G"
            elif maze.grid[r][c] == -1:
                row_str += "#"
            elif maze.grid[r][c] == 100:
                row_str += "|"
            else:
                row_str += "."
        print(f"r{r}: {row_str}")

if __name__ == "__main__":
    # Create maze and print it
    maze = Maze()
    print_maze(maze)
    
    # Run all algorithms
    results = run_all_algorithms()
    
    # Print results table
    print_results_table(results)
    
    # Additional analysis
    print(f"\nAnalysis:")
    print(f"- Start position: {maze.start}")
    print(f"- Goal position: {maze.goal}")
    print(f"- Manhattan distance (heuristic): {maze.manhattan_distance(*maze.start, *maze.goal)}")
    
    # Find best performing algorithm
    best_time = min(results.values(), key=lambda x: x['execution_time'])
    best_cost = min(results.values(), key=lambda x: x['path_cost'])
    best_nodes = min(results.values(), key=lambda x: x['nodes_expanded'])
    
    print(f"\nBest Performance:")
    for name, result in results.items():
        if result == best_time:
            print(f"- Fastest execution: {name} ({result['execution_time']:.2f} ms)")
        if result == best_cost:
            print(f"- Lowest path cost: {name} ({result['path_cost']})")
        if result == best_nodes:
            print(f"- Fewest nodes expanded: {name} ({result['nodes_expanded']})")
