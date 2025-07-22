# Slitherlink Solver

Slitherlink Solver is a desktop application for solving and generating the Slitherlink logic puzzle. The program allows creating boards, manually marking edges, automatically solving using a SAT solver, and visualizing the results.

---

## Prerequisites

- Python 3.10 or higher  
- Lingeling SAT solver (available in your system PATH)  
- `tkinter` library (included in standard Python installations)  
- Access to terminal / console  

---

## Installation and Configuration

1. **Download the project**  
   - Clone the repository or download the source files:
     ```bash
     git clone https://github.com/SebastianUfniarz/Slitherlink_SAT-solver.git
     ```

2. **Install Lingeling solver**  
   - Download Lingeling from the official website and place it in a directory accessible from your terminal.

3. **Run the application**  
   - In the project directory run:
     ```bash
     python main.py
     ```

---

## Usage

- **Generate a board**  
  Enter the board width, height, and clue density percentage in the GUI, then click "Generate".

- **Load board from file**  
  Click "Load from File" and select a text file containing the board.

- **Manually mark edges**  
  Click on edges between dots to toggle them on or off.

- **Automatically solve**  
  Click "Solve" — the program will use the SAT solver to find a solution.

- **Check solution**  
  Click "Check Solution" to verify if the marked edges form a correct solution.

- **Reset board**  
  Click "Reset" to clear all markings.

---

## Board file format

Boards are saved in a simple text format where:  
- `.` denotes an empty cell (no clue),  
- digits `0` to `3` specify the required number of edges around that cell.

Example: <br>
..... <br>
.1... <br>
..1.. <br>
..... <br>
..... <br>

## Project structure

- `slitherlink_solver.py` — logic for generating SAT clauses and invoking the solver.  
- `main.py` — graphical user interface for drawing the board and interacting with the user.  
- Board files — text files in the format described above.
