from itertools import combinations
from collections import deque
from pysat.solvers import Lingeling
import random

class SlitherlinkSolver:
    def __init__(self):
        self.cells = None
        self.width = None
        self.height = None
        self.cell_constraints = []
        self.loop_constraints = []
        self.solution = None

    def read_problem(self, filename):
        with open(filename) as fin:
            self.cells = []
            expected_width = None
            has_digit = False

            for line_number, line in enumerate(fin, start=1):
                row = []
                for char in line:
                    if char == '.':
                        row.append(None)
                    elif char.isdigit():
                        value = int(char)
                        if value < 0 or value > 3:
                            raise ValueError(
                                f"Invalid digit '{char}' at line {line_number}: must be between 0 and 3.")
                        row.append(value)
                        has_digit = True

                if row:
                    if expected_width is None:
                        expected_width = len(row)
                    elif len(row) != expected_width:
                        raise ValueError(
                            f"Inconsistent row length at line {line_number}: expected {expected_width}, got {len(row)}.")
                    self.cells.append(row)

            if not self.cells:
                raise ValueError("File does not contain any valid grid data.")

            self.width = expected_width
            self.height = len(self.cells)

            if self.width < 2 or self.height < 2:
                raise ValueError(f"Grid must be at least 2x2. Got {self.height}x{self.width}.")

            if not has_digit:
                raise ValueError("Grid must contain at least one clue (digit 0–3).")


    def get_cell_edges(self, cell_id):
        cell_row = cell_id // self.width
        cell_col = cell_id % self.height
        num_horizontal = self.height * (self.width + 1)
        upper_edge = cell_id
        lower_edge = upper_edge + self.width
        left_edge = num_horizontal + ((cell_row * (self.width + 1)) + cell_col)
        right_edge = left_edge + 1
        return [upper_edge, lower_edge, left_edge, right_edge]

    def get_corner_vertices(self, vertex_id):
        col = vertex_id % (self.width + 1)
        row = vertex_id // (self.width + 1)
        upper_edge = lower_edge = left_edge = right_edge = None
        distance = self.width * (self.height + 1)
        if row > 0:
            upper_edge = distance + vertex_id - (self.width + 1)
        if row < self.height:
            lower_edge = distance + vertex_id
        if col > 0:
            left_edge = (self.width * row) + col - 1
        if col < self.width:
            right_edge = (self.width * row) + col
        return [v for v in [upper_edge, lower_edge, left_edge, right_edge] if v is not None]

    def get_adjacent_edges(self, edge_id):
        num_vertices = (self.width + 1) * (self.height + 1)
        v1, v2 = [vertex_id for vertex_id in range(num_vertices)
                  if edge_id in self.get_corner_vertices(vertex_id)]
        edge1 = [edge for edge in self.get_corner_vertices(v1)
                 if edge != edge_id]
        edge2 = [edge for edge in self.get_corner_vertices(v2)
                 if edge != edge_id]
        return edge1 + edge2

    def get_edge_vertices(self, edge_id):
        if edge_id < self.height * (self.width + 1):
            row = edge_id // self.width
            col = edge_id % self.width
            v1 = row * (self.width + 1) + col
            v2 = v1 + 1
        else:
            edge_id -= self.height * (self.width + 1)
            row = edge_id // (self.width + 1)
            col = edge_id % (self.width + 1)
            v1 = row * (self.width + 1) + col
            v2 = v1 + (self.width + 1)
        return v1, v2

    def generate_cell_constraints(self):
        def exactly_k(k, edges):
            """Generuje klauzule wymuszające, że dokładnie k krawędzi jest aktywnych."""
            from itertools import combinations
            n = len(edges)
            clauses = []
            
            for comb in combinations(edges, n - k + 1):
                clauses.append(list(comb))

            for comb in combinations(edges, k + 1):
                clauses.append([-edge for edge in comb])
            
            return clauses

        self.cell_constraints = []
        cell_id = -1
        
        for row in range(self.height):
            for col in range(self.width):
                cell_id += 1
                cell_value = self.cells[row][col]
                if cell_value is not None:
                    edges = [1 + k for k in self.get_cell_edges(cell_id)]
                    clauses = exactly_k(cell_value, edges)
                    self.cell_constraints += clauses

    def generate_loop_constraints(self):
        def two(k1, k2):
            """Generuje ograniczenia dla wierzchołka w rogu siatki."""
            return [[-k1, k2], [k1, -k2]]

        def three(k1, k2, k3):
            """Generuje ograniczenia dla wierzchołka na krawędzi siatki."""
            return [[-k1, k2, k3],
                    [k1, -k2, k3],
                    [k1, k2, -k3],
                    [-k1, -k2, -k3]]

        def four(k1, k2, k3, k4):
            """Generuje ograniczenia dla wierzchołka wewnątrz siatki."""
            return [[-k1, k2, k3, k4],
                    [k1, -k2, k3, k4],
                    [k1, k2, -k3, k4],
                    [k1, k2, k3, -k4],
                    [-k1, -k2, -k3],
                    [-k1, -k2, -k4],
                    [-k1, -k3, -k4],
                    [-k2, -k3, -k4]]

        vertex_constraints = {
            2: two,
            3: three,
            4: four
        }

        corner_vertices = (self.width + 1) * (self.height + 1)
        self.loop_constraints = []

        for vertex_id in range(corner_vertices):
            vertexes = [1 + k for k in self.get_corner_vertices(vertex_id)]
            num_edges = len(vertexes)
            if num_edges in vertex_constraints:
                clauses = vertex_constraints[num_edges](*vertexes)
                self.loop_constraints.extend(clauses)

    def call_sat_solver(self):       
        
        constraints = self.cell_constraints + self.loop_constraints
    
        with Lingeling() as solver:
            solver.append_formula(constraints)
            
            found = False
            for solution in solver.enum_models():
                test_solution = [edge for edge in solution if edge > 0]
                if self.bfs_check_loop(test_solution):
                    self.solution = test_solution
                    found = True
                    break
                
        if not found:
            print("No solution")       
    
    def generate_random_grid(self, size=(5, 5), fill_percentage=0.3):       
        self.height, self.width = size
        self.cells = [[None for _ in range(self.width)] for _ in range(self.height)]
        
        num_cells = int(self.height * self.width * fill_percentage)
        positions = random.sample([(i, j) for i in range(self.height) for j in range(self.width)], num_cells)
        
        for i, j in positions:
            self.cells[i][j] = random.randint(0, 3)
        
        self.generate_cell_constraints()
        self.generate_loop_constraints()
        self.call_sat_solver()
        
        return self.solution is not None

    def save_generated_grid(self, filename):
        with open(filename, 'w') as f:
            for row in self.cells:
                line = ''.join(['.' if cell is None else str(cell) for cell in row])
                f.write(line + '\n')
                
    def bfs_check_loop(self, solution):
        if not solution:
            return False
        solution = {edge - 1 for edge in solution} 
        queue = deque([next(iter(solution))])
        visited = set()

        while queue:
            edge = queue.popleft()
            visited.add(edge)
            neighbors = [e for e in self.get_adjacent_edges(edge) if e in solution and e not in visited]
            queue.extend(neighbors)

        return len(visited) == len(solution)