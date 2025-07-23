# Slitherlink Solver

Slitherlink Solver is a desktop application for solving and generating the Slitherlink logic puzzle. The program allows creating boards, manually marking edges, automatically solving using a SAT solver, and visualizing the results.

Slitherlink is a logic puzzle game in which the goal is to create a loop on a grid according to specific rules. Here are the main rules of the game:
Grid: The game is played on a grid composed of empty cells, edges, and numbers on some of the cells. It is usually a square grid, e.g., 6x6.
Numbers in the cells: Some cells contain numbers (from 0 to 3). A number indicates how many of the edges surrounding that cell must be part of the loop.
The loop: The objective is to draw a single closed and continuous loop on the grid, using the edges in such a way that it satisfies the conditions given by the numbers in the cells.
No crossing or branching: The loop cannot cross itself or branch off in multiple directions.
No double edges: An edge can only be used once as part of the loop.

---

## Prerequisites

- Python 3.10.11  
- Lingeling SAT solver 1.8.dev14 should be working with higher versions.
- `tkinter` library 8.6.12
- Access to terminal / console  

---

## Installation and Configuration

1. **Download the project**  
   - Clone the repository or download the source files:
     ```bash
     git clone https://github.com/SebastianUfniarz/Slitherlink_SAT-solver.git
     ```

2. **Install Lingeling solver**  
   - Download Lingeling SAT-solver.

3. **Run the application**  
   - In the project directory run:
     ```bash
     python main.py
     ```

---

## Usage

- **Generate a board**  
  Enter the board width, height, then click "Generate" (you can change density in the on_generate_click function).

- **Load board from file**  
   The input file shown in the example below is based on a rectangular grid, where each dot (.) represents a single cell on the board. Numerical values from 0 to 3 indicate the number of edges that should surround the given cell, in accordance with the rules of the Slitherlink puzzle. A dot (.) signifies the absence of a number, meaning the cell has no enforced constraint. Each line in the text file corresponds to one row of the board, and similarly, the columns in the file represent the respective columns of the board.
Example: <br>
..... <br>
.1... <br>
..1.. <br>
..... <br>
..... <br>

- **Manually mark edges**  
  Click on edges between dots to toggle them on or off.

- **Automatically solve**  
  Click "Solve" — the program will use the SAT solver to find a solution.

- **Check solution**  
  Click "Check Solution" to verify if the marked edges form a correct solution.

- **Reset board**  
  Click "Reset" to clear all markings.

---

## Project structure

- `slitherlink_solver.py` — logic for generating SAT clauses and invoking the solver.  
- `main.py` — graphical user interface for drawing the board and interacting with the user.  
- Board files — text files in the format described above.
