# sat_solver_benchmark.py
import time
import random
import argparse
import os
import matplotlib.pyplot as plt
import csv


# ------------------ CNF Parser ------------------ #
def parse_dimacs(filename):
    clauses = []
    num_vars = 0
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('c'):
                continue
            elif line.startswith('p cnf'):
                num_vars = int(line.split()[2])
            else:
                clause = list(map(int, line.strip().split()))
                if clause[-1] == 0:
                    clause = clause[:-1]
                clauses.append(clause)
    return clauses, num_vars


# ------------------ Davis-Putnam (DP) ------------------ #
def dp(clauses, symbols):
    if not clauses:
        return True
    if any([clause == [] for clause in clauses]):
        return False

    symbol = symbols[0]
    rest = symbols[1:]

    def assign(value):
        new_clauses = []
        for clause in clauses:
            if symbol * value in clause:
                continue
            new_clause = [x for x in clause if x != -symbol * value]
            new_clauses.append(new_clause)
        return new_clauses

    return dp(assign(1), rest) or dp(assign(-1), rest)


# ------------------ DPLL ------------------ #
def dpll(clauses, assignment={}):
    if all([any(lit in assignment and assignment[lit] for lit in clause) for clause in clauses]):
        return True

    if any([all((lit in assignment and not assignment[lit]) for lit in clause) for clause in clauses]):
        return False

    unassigned = {abs(lit) for clause in clauses for lit in clause} - assignment.keys()
    if not unassigned:
        return True

    var = unassigned.pop()
    for val in [True, False]:
        assignment[var] = val
        assignment[-var] = not val
        if dpll(clauses, assignment):
            return True
        del assignment[var]
        del assignment[-var]
    return False


# ------------------ CDCL (Simplified) ------------------ #
def cdcl(clauses, num_vars):
    assignment = {}
    decision_level = 0

    def unit_propagate():
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                unassigned = [l for l in clause if abs(l) not in assignment]
                if len(unassigned) == 1:
                    lit = unassigned[0]
                    assignment[abs(lit)] = lit > 0
                    changed = True
                elif all(assignment.get(abs(l), l < 0) == (l < 0) for l in clause):
                    return False
        return True

    def backtrack(level):
        nonlocal assignment
        assignment = {k: v for k, v in assignment.items() if k <= level}

    def choose_literal():
        for var in range(1, num_vars + 1):
            if var not in assignment:
                return var
        return None

    while True:
        if unit_propagate():
            if all(any(assignment.get(abs(l), l > 0) == (l > 0) for l in clause) for clause in clauses):
                return True
            decision_level += 1
            var = choose_literal()
            if var is None:
                return True
            assignment[var] = random.choice([True, False])
        else:
            if decision_level == 0:
                return False
            backtrack(decision_level - 1)
            decision_level -= 1


# ------------------ Pigeonhole Principle Generator ------------------ #
def generate_pigeonhole_cnf(n, filename='pigeonhole.cnf'):
    clauses = []
    vars_map = lambda p, h: p * n + h + 1

    for p in range(n + 1):
        clauses.append([vars_map(p, h) for h in range(n)])

    for h in range(n):
        for p1 in range(n + 1):
            for p2 in range(p1 + 1, n + 1):
                clauses.append([-vars_map(p1, h), -vars_map(p2, h)])

    with open(filename, 'w') as f:
        f.write(f"p cnf {n * (n + 1)} {len(clauses)}\n")
        for clause in clauses:
            f.write(' '.join(map(str, clause)) + ' 0\n')


# ------------------ Random 3-SAT Generator ------------------ #
def generate_random_3sat(num_vars, num_clauses, filename='random.cnf'):
    clauses = []
    for _ in range(num_clauses):
        clause = random.sample(range(1, num_vars + 1), 3)
        clause = [x if random.random() < 0.5 else -x for x in clause]
        clauses.append(clause)

    with open(filename, 'w') as f:
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        for clause in clauses:
            f.write(' '.join(map(str, clause)) + ' 0\n')


# ------------------ Benchmarking ------------------ #
def benchmark_solver(solver, clauses, num_vars, name):
    start = time.time()
    if name == "DP":
        result = solver(clauses, list(range(1, num_vars + 1)))
    elif name == "CDCL":
        result = solver(clauses, num_vars)
    else:
        result = solver(clauses, {})
    duration = time.time() - start
    return name, 'SAT' if result else 'UNSAT', duration


# ------------------ Visualization in PDF ------------------ #

# def plot_results(results, filename="benchmark_plot.pdf"):
#     for solver_name, timings in results.items():
#         sizes = [x[0] for x in timings]
#         times = [x[1] for x in timings]
#         plt.plot(sizes, times, label=solver_name)
#
#     plt.xlabel("Problem Size (n for pigeonhole, vars for 3SAT)")
#     plt.ylabel("Time (s)")
#     plt.title("SAT Solver Benchmark")
#     plt.legend()
#     plt.grid(True)
#     plt.tight_layout()
#     plt.savefig(filename)
#     print(f"Plot saved to {filename}")

# ------------ SHOW GRID ON SCREEN ------------ #

def plot_results(results):
    for solver_name, timings in results.items():
        sizes = [x[0] for x in timings]
        times = [x[1] for x in timings]
        plt.plot(sizes, times, label=solver_name)

    plt.xlabel("Problem Size (n for pigeonhole, vars for 3SAT)")
    plt.ylabel("Time (s)")
    plt.title("SAT Solver Benchmark")
    plt.legend()
    plt.grid(True)
    plt.show()


# ------------------ Export to LaTeX ------------------ #

def export_results(results, csv_file="benchmark_results.csv", tex_file="benchmark_table.tex"):
    with open(csv_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Problem Size", "DP Time (s)", "DPLL Time (s)", "CDCL Time (s)"])

        sizes = sorted({size for timing in results.values() for size, _ in timing})
        for size in sizes:
            row = [size]
            for solver in ["DP", "DPLL", "CDCL"]:
                time_val = next((t for s, t in results[solver] if s == size), "N/A")
                row.append(f"{time_val:.6f}" if isinstance(time_val, float) else time_val)
            writer.writerow(row)

    with open(tex_file, "w") as tex:
        tex.write("\\begin{table}[H]\n\\centering\n")
        tex.write("\\begin{tabular}{|c|c|c|c|}\n\\hline\n")
        tex.write("Problem Size & DP Time (s) & DPLL Time (s) & CDCL Time (s) \\\\\n\\hline\n")

        for size in sizes:
            row = [str(size)]
            for solver in ["DP", "DPLL", "CDCL"]:
                time_val = next((t for s, t in results[solver] if s == size), "N/A")
                row.append(f"{time_val:.6f}" if isinstance(time_val, float) else time_val)
            tex.write(" & ".join(row) + " \\\\\n")

        tex.write("\\hline\n\\end{tabular}\n")
        tex.write("\\caption{Benchmark results for SAT solvers}\n")
        tex.write("\\label{tab:sat_benchmarks}\n")
        tex.write("\\end{table}\n")
    print(f"Exported benchmark results to {csv_file} and {tex_file}")


# ------------------ Main ------------------ #
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", choices=["pigeonhole", "3sat"], required=True)
    parser.add_argument("--min", type=int, default=2)
    parser.add_argument("--max", type=int, default=6)
    args = parser.parse_args()

    results = {"DP": [], "DPLL": [], "CDCL": []}

    for n in range(args.min, args.max + 1):
        if args.test == "pigeonhole":
            filename = f"ph_{n}.cnf"
            generate_pigeonhole_cnf(n, filename)
        else:
            filename = f"3sat_{n}.cnf"
            generate_random_3sat(n * 3, n * 5, filename)  # 3-SAT formula size

        clauses, num_vars = parse_dimacs(filename)

        for solver_func, name in [(dp, "DP"), (dpll, "DPLL"), (cdcl, "CDCL")]:
            solver_name, result, time_taken = benchmark_solver(solver_func, clauses, num_vars, name)
            print(f"{solver_name} | Size {n}: {result} in {time_taken:.6f}s")
            results[name].append((n, time_taken))

    plot_results(results)
    export_results(results)

    # Clean up generated files
    for n in range(args.min, args.max + 1):
        try:
            os.remove(f"ph_{n}.cnf")
            os.remove(f"3sat_{n}.cnf")
        except FileNotFoundError:
            pass
