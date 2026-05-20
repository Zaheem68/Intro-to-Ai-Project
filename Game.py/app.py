from flask import Flask, render_template, request, jsonify
import time

app = Flask(__name__)

# --- DSA Backtracking Logic for API ---
def get_solve_steps(n_grid, n_queens, locked_queens):
    steps = []
    sim_board = [[0]*n_grid for _ in range(n_grid)]
    locked_rows = set()
    
    # Place user's manual queens on the board
    for r, c in locked_queens:
        sim_board[r][c] = 1
        locked_rows.add(r)
        
    sim_queens = list(locked_queens)
    found_solution = False

    def is_safe(r, c):
        for i in range(n_grid):
            if sim_board[i][c] and i != r: return False
            if sim_board[r][i] and i != c: return False
        for d in range(1, n_grid):
            if r-d >= 0 and c-d >= 0 and sim_board[r-d][c-d]: return False
            if r-d >= 0 and c+d < n_grid and sim_board[r-d][c+d]: return False
            if r+d < n_grid and c-d >= 0 and sim_board[r+d][c-d]: return False
            if r+d < n_grid and c+d < n_grid and sim_board[r+d][c+d]: return False
        return True

    def backtrack(row):
        nonlocal found_solution
        if found_solution: return True
        
        # Success: All queens placed
        if len(sim_queens) == n_queens:
            found_solution = True
            steps.append({"type": "solved", "queensSnap": [list(q) for q in sim_queens]})
            return True
            
        # Pigeonhole Principle: Ran out of rows before placing all queens
        if row >= n_grid:
            steps.append({"type": "pigeonhole_fail", "queensSnap": [list(q) for q in sim_queens]})
            return True 

        # Skip rows that user already locked
        if row in locked_rows:
            return backtrack(row + 1)
            
        for col in range(n_grid):
            steps.append({"type": "try", "r": row, "c": col, "queensSnap": [list(q) for q in sim_queens]})
            if is_safe(row, col):
                sim_board[row][col] = 1
                sim_queens.append([row, col])
                steps.append({"type": "place", "r": row, "c": col, "queensSnap": [list(q) for q in sim_queens]})
                
                if backtrack(row + 1): return True
                
                sim_board[row][col] = 0
                sim_queens.pop()
                steps.append({"type": "backtrack", "r": row, "c": col, "queensSnap": [list(q) for q in sim_queens]})
        return False

    success = backtrack(0)
    
    # Dead end caused by manual placements
    if not success and (len(steps) == 0 or steps[-1]["type"] != "pigeonhole_fail"):
        steps.append({"type": "unsolvable_manual"})
        
    return steps

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/solve', methods=['POST'])
def solve():
    data = request.json
    n_grid = data.get('n_grid', 14)
    n_queens = data.get('n_queens', 15)
    locked_queens = data.get('queens', [])
    
    start_time = time.time()
    steps = get_solve_steps(n_grid, n_queens, locked_queens)
    compute_time = (time.time() - start_time) * 1000 # MS
    
    return jsonify({
        'steps': steps,
        'computeTimeMs': compute_time
    })

if __name__ == '__main__':
    app.run(debug=True)