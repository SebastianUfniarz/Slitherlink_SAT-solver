import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from slitherlink_solver import SlitherlinkSolver
from collections import defaultdict

class SlitherlinkGUI:
    def __init__(self, solver):
        self.solver = solver
        self.root = tk.Tk()
        self.canvas = None
        self.scrollable_frame = None
        self.solve_button = None
        self.check_button = None
        self.reset_button = None
        self.vertical_scrollbar = None
        self.selected_edges = set()
        self.edge_lines = {}
        self.solution_lines = []
        self.current_solution = None

        self.root.title("Slitherlink Solver")
        self.root.geometry("1200x1000")
        self.root.configure(bg="#f0f0f0")

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.solve_button = ttk.Button(
            self.button_frame,
            text="Solve",
            command=self.on_solve_click,
            style="TButton"
        )
        self.solve_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.check_button = ttk.Button(
            self.button_frame,
            text="Check Solution",
            command=self.on_check_click,
            style="TButton"
        )
        self.check_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.reset_button = ttk.Button(
            self.button_frame,
            text="Reset",
            command=self.on_reset_click,
            style="TButton"
        )
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.size_frame = ttk.Frame(self.button_frame)
        self.size_frame.pack(side=tk.LEFT, padx=10)

        ttk.Label(self.size_frame, text="Height:", font=("Arial", 10)).grid(row=0, column=0, padx=2)
        self.height_entry = ttk.Entry(self.size_frame, width=5)
        self.height_entry.grid(row=0, column=1, padx=2)
        self.height_entry.insert(0, "5")

        ttk.Label(self.size_frame, text="Width:", font=("Arial", 10)).grid(row=0, column=2, padx=2)
        self.width_entry = ttk.Entry(self.size_frame, width=5)
        self.width_entry.grid(row=0, column=3, padx=2)
        self.width_entry.insert(0, "5")

        self.generate_button = ttk.Button(
            self.button_frame,
            text="Generate",
            command=self.on_generate_click,
            style="TButton"
        )
        self.generate_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.load_button = ttk.Button(
            self.button_frame,
            text="Load from File",
            command=self.on_load_click,
            style="TButton"
        )
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 12), padding=10)

        self.scrollable_frame = ttk.Frame(self.root)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.scrollable_frame, bg="white")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.vertical_scrollbar = ttk.Scrollbar(
            self.scrollable_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        self.vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.vertical_scrollbar.set)

        self.canvas.bind("<Configure>", self.update_scrollregion)
        self.canvas.bind("<Button-1>", self.toggle_edge)

        self.draw_grid()

    def on_generate_click(self):
        try:
            height = int(self.height_entry.get())
            width = int(self.width_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid board size.")
            return

        if height < 2 or width < 2:
            messagebox.showwarning("Limit", "Minimum board size is 2x2.")
            return
        if height > 15 or width > 15:
            messagebox.showwarning("Limit", "Maximum board size is 15x15.")
            return

        while True:
            generator = SlitherlinkSolver()

            if generator.generate_random_grid(size=(height, width), fill_percentage=0.35):
                generator.save_generated_grid("generated.txt")

                self.solver = SlitherlinkSolver()
                self.solver.read_problem("generated.txt")
                self.current_solution = None
                self.on_reset_click()
                self.canvas.delete("all")
                self.draw_grid()

                messagebox.showinfo("Success", f"Successfully generated a valid {height}x{width} board!")
                break

    def on_load_click(self):
        filepath = filedialog.askopenfilename(
            title="Select Slitherlink grid file",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not filepath:
            return

        try:
            self.solver = SlitherlinkSolver()
            self.solver.read_problem(filepath)
            self.current_solution = None
            self.on_reset_click()
            self.canvas.delete("all")
            self.draw_grid()
            messagebox.showinfo("Success", f"Loaded board from file:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file:\n{e}")

    def on_reset_click(self):
        for line in self.solution_lines:
            self.canvas.delete(line)
        self.solution_lines = []

        self.selected_edges.clear()
        for line_id in self.edge_lines.values():
            self.canvas.delete(line_id)
        self.edge_lines = {}

        self.current_solution = None

    def draw_solution(self):
        if not self.current_solution:
            messagebox.showinfo("Info", "No solution to draw.")
            return

        margin = 20
        cell_size = 40

        for line in self.solution_lines:
            self.canvas.delete(line)
        self.solution_lines = []

        def horizontal_edge(k):
            col_f = k % self.solver.width
            row_l = k // self.solver.width
            y = margin + cell_size * row_l
            x1 = margin + cell_size * col_f
            x2 = margin + cell_size * (col_f + 1)
            line = self.canvas.create_line(x1, y, x2, y, width=3, fill="blue")
            self.solution_lines.append(line)

        def vertical_edge(k):
            row_f = k // (self.solver.width + 1)
            col_l = k % (self.solver.width + 1)
            y1 = margin + cell_size * row_f
            y2 = margin + cell_size * (row_f + 1)
            x = margin + cell_size * col_l
            line = self.canvas.create_line(x, y1, x, y2, width=3, fill="blue")
            self.solution_lines.append(line)

        horizontal_limit = self.solver.height * (self.solver.width + 1)
        horizontals = [k - 1 for k in self.current_solution if k <= horizontal_limit]
        verticals = [k - horizontal_limit - 1 for k in self.current_solution if k > horizontal_limit]

        for h_edge in horizontals:
            horizontal_edge(k=h_edge)
        for v_edge in verticals:
            vertical_edge(k=v_edge)

    def on_solve_click(self):
        if not self.current_solution:
            self.solver.generate_cell_constraints()
            self.solver.generate_loop_constraints()
            self.solver.call_sat_solver()
            if self.solver.solution:
                self.current_solution = self.solver.solution.copy()
                self.draw_solution()
            else:
                messagebox.showwarning("Warning", "No solution found for this grid.")
        else:
            self.draw_solution()

    def on_check_click(self):
        if self.current_solution:
            if self.check_solution(self.current_solution):
                messagebox.showinfo("Check", "Solver solution is correct!")
            else:
                messagebox.showwarning("Check", "Solver solution is NOT correct!")
        elif self.selected_edges:
            if self.check_solution(self.selected_edges, manual=True):
                messagebox.showinfo("Check", "Manual solution is correct!")
            else:
                messagebox.showwarning("Check", "Manual solution is NOT correct!")
        else:
            messagebox.showinfo("Check", "No solution or manual edges to check.")

    def check_solution(self, edges, manual=False):
        if manual:
            edge_set = edges
        else:
            edge_set = {e - 1 for e in edges}

        for row in range(self.solver.height):
            for col in range(self.solver.width):
                cell_value = self.solver.cells[row][col]
                if cell_value is not None:
                    cell_id = row * self.solver.width + col
                    cell_edges = self.solver.get_cell_edges(cell_id)
                    selected_count = sum(1 for edge in cell_edges if edge in edge_set)
                    if selected_count != cell_value:
                        return False

        return self.check_loop_connectivity(edge_set)

    def check_loop_connectivity(self, edge_set):
        if not edge_set:
            return False

        graph = {}
        for edge in edge_set:
            v1, v2 = self.solver.get_edge_vertices(edge)
            if v1 not in graph:
                graph[v1] = set()
            if v2 not in graph:
                graph[v2] = set()
            graph[v1].add(v2)
            graph[v2].add(v1)

        visited = set()
        stack = [next(iter(graph))]

        while stack:
            vertex = stack.pop()
            if vertex in visited:
                continue
            visited.add(vertex)
            if len(graph[vertex]) != 2:
                return False
            stack.extend(graph[vertex] - visited)

        return len(visited) == len(graph)

    def toggle_edge(self, event):
        x, y = event.x, event.y
        margin = 20
        cell_size = 40

        for k in range(self.solver.height * (self.solver.width + 1)):
            row = k // self.solver.width
            col = k % self.solver.width
            y_edge = margin + cell_size * row
            x1 = margin + cell_size * col
            x2 = margin + cell_size * (col + 1)
            if abs(y - y_edge) < 5 and x1 <= x <= x2:
                if k in self.selected_edges:
                    self.selected_edges.remove(k)
                    self.canvas.delete(self.edge_lines[k])
                else:
                    self.selected_edges.add(k)
                    self.edge_lines[k] = self.canvas.create_line(x1, y_edge, x2, y_edge, width=3, fill="red")
                return

        for k in range(self.solver.width * (self.solver.height + 1)):
            row = k // (self.solver.width + 1)
            col = k % (self.solver.width + 1)
            x_edge = margin + cell_size * col
            y1 = margin + cell_size * row
            y2 = margin + cell_size * (row + 1)
            index = k + self.solver.height * (self.solver.width + 1)
            if abs(x - x_edge) < 5 and y1 <= y <= y2:
                if index in self.selected_edges:
                    self.selected_edges.remove(index)
                    self.canvas.delete(self.edge_lines[index])
                else:
                    self.selected_edges.add(index)
                    self.edge_lines[index] = self.canvas.create_line(x_edge, y1, x_edge, y2, width=3, fill="red")
                return

    def update_scrollregion(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def draw_grid(self):
        margin = 20
        cell_size = 40

        def draw_numbers():
            for row_index, row in enumerate(self.solver.cells):
                for col_index, val in enumerate(row):
                    if val is not None:
                        y = margin + cell_size * row_index + cell_size // 2
                        x = margin + cell_size * col_index + cell_size // 2
                        self.canvas.create_text(x, y, text=str(val), font=('Arial', 14, 'bold'))

        def draw_corners():
            for row in range(self.solver.height + 1):
                for col in range(self.solver.width + 1):
                    x = margin + cell_size * col
                    y = margin + cell_size * row
                    self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill='black')

        draw_numbers()
        draw_corners()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    solver = SlitherlinkSolver()
    solver.read_problem("55easy.txt")
    gui = SlitherlinkGUI(solver)
    gui.run()
