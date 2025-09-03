# CS301 Project – Maximum Cut Problem

## Overview
This repository contains my project report and implementation for the **CS301 (2024–2025 Summer)** course.  
The project focuses on the **Maximum Cut Problem**, one of the classical NP-hard problems in computer science and optimization.  

The **goal** of the problem is:  
> Given an undirected, unweighted graph \( G = (V, E) \), partition the vertices into two disjoint sets such that the number of crossing edges is maximized.  

This problem arises in areas such as VLSI design, statistical physics (Ising model), clustering in machine learning, and network optimization.

---

## Algorithms Implemented

### 1. Brute-Force Algorithm
- Enumerates all possible partitions of the vertex set.  
- Guarantees the optimal solution.  
- **Time complexity:**  
  \[
  O(2^n \cdot |E|)
  \]
- Practical only for very small graphs (up to ~20 vertices).

### 2. Heuristic Algorithm
- **Multi-start 1-flip local search approach**:  
  - Start from a random cut.  
  - Iteratively flip vertices if the cut improves.  
  - Stop when no further improvements are possible.  
  - Restart multiple times and take the best cut.  
- Much faster, scales to graphs with thousands of vertices.  
- **Time complexity:**  
  Typically close to \[
  O(|E|)
  \] per restart.

---

## Sample Generation

We generate random graphs using two Erdős–Rényi models:

1. **\( G(n,p) \) model**  
   - \( n \) vertices, each edge appears independently with probability \( p \).  
   - Used for density sweeps with \( p \in \{0.1, 0.2, \dots, 0.9\} \).

2. **\( G(n,m) \) model**  
   - \( n \) vertices, exactly \( m \) edges chosen uniformly at random.  
   - We test at \( 25\%, 50\%, 75\% \) of \( \binom{n}{2} \).  
   - Implemented efficiently using **Floyd’s selection method** to avoid storing all possible edges.

For averaging, each configuration was run with **5 random seeds**.

---

## Performance Testing

- Goal: Measure runtime scaling of the heuristic.  
- Setup: \( G(n, 0.5) \) graphs with sizes up to \( n = 3000 \).  
- Repetitions: 30 runs for small sizes, fewer runs for large \( n \).  
- Metrics: mean runtime, variance, 90% confidence intervals.  

**Findings:**
- Runtime grows polynomially, consistent with theoretical complexity.  
- Experimental curve fitting shows exponent ≈ 1.69.  
- For \( n \leq 2000 \), runtime < 1 second; even for \( n = 3000 \), runtime ≈ 1.8 seconds.  
- Confirms the heuristic is highly scalable.

---

## Quality Testing

- Goal: Compare heuristic vs brute force on small graphs.  
- Setup: \( G(n,0.5) \), with \( n = 10,12,14,16,18 \).  
- Metrics:  
  - **Ratio** \( \rho = \frac{C_H}{C_{BF}} \)  
  - **Absolute gap** \( \Delta = C_{BF} - C_H \)  
  - **Failure rate** (% of runs where heuristic < optimal).  

**Findings:**
- For small \( n \), heuristic matches brute force (failure rate = 0%).  
- At \( n=18 \), failure rate increases to ≈ 33%.  
- Overall, heuristic is **near-optimal** and practical when brute force is infeasible.

---
