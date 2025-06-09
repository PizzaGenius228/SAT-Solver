# SAT-Solver 🔍

A benchmarking and comparative analysis framework for classical SAT solving algorithms — including **Davis-Putnam (DP)**, **Davis-Putnam-Logemann-Loveland (DPLL)**, and **Conflict-Driven Clause Learning (CDCL)** — implemented in Python.

## 📘 Overview

This project provides lightweight, educational implementations of:
- **Complete SAT Solvers**: DP, DPLL, CDCL
- **Benchmarking Scripts**
- **CNF Instance Generators**
- **Plotting and CSV output for runtime comparisons**

It is part of a research project comparing theoretical and practical performance of SAT solving algorithms.

## 📁 Repository Structure

```
SAT-Solver/
├── Sat Solver/
│   ├── benchmark_plot.pdf        # Plot of execution time vs. problem size
│   ├── benchmark_results.csv     # Benchmark results (CSV)
│   ├── commands.txt              # Command-line usage examples
│   └── sat_bechmark.py           # Main benchmarking script
├── README.md                     # This file
```

> ✅ Note: The main script is named `sat_bechmark.py` (with a typo in "benchmark").

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.7+
- No external libraries required (pure Python)

### 🔧 Run Benchmarks

Run default benchmark:
```bash
python "Sat Solver/sat_bechmark.py"
```

Run pigeonhole benchmarks (n from 2 to 6):
```bash
python "Sat Solver/sat_bechmark.py" --test pigeonhole --min 2 --max 6
```

Run random 3-SAT benchmarks (variables from 10 to 20):
```bash
python "Sat Solver/sat_bechmark.py" --test 3sat --min 10 --max 20
```

### 📊 View Results

- View `benchmark_results.csv` for raw data.
- View `benchmark_plot.pdf` for visual performance comparison of DP, DPLL, and CDCL.

## 📚 Reference

This repository supports the academic paper:

> **SAT Solving: Benchmarking and Comparing Complete and Incomplete Algorithms**  
> Kristof Alfred-Roland, 2025

## 🌐 GitHub

🔗 [https://github.com/PizzaGenius228/SAT-Solver](https://github.com/PizzaGenius228/SAT-Solver)
