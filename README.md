```markdown
# Ant Colony Routing Optimization

## Executive Summary
This project simulates the evacuation of an ant colony through a network of rooms and tunnels. The objective is to compute the optimal routing of a given number of ants from a starting node (`Sv`) to a destination node (`Sd`), while strictly enforcing the concurrency capacity constraints of each intermediate node.

This repository serves as a comparative study of two distinct graph theory algorithms solving a network flow problem. It highlights the software engineering trade-offs between local dynamic decision-making and global capacity pre-calculation.

---

## System Architecture

The repository is structured to separate domain logic, resolution engines, and datasets:

```text
.
├── code/
│   ├── classes_ants.py        # Shared data models (OOP) and file parsing
│   ├── algo_dynamique.py      # Opportunistic routing engine (BFS/Greedy)
│   └── algo_flot_max.py       # Global capacity routing engine (Max Flow)
│
├── data/                      # Network topology datasets (.txt)
│   ├── fourmiliere_un.txt
│   ├── fourmiliere_trois.txt
│   └── salle_d_at-ant.txt     
│
└── ressources/                # Documentation and assets

```

---

## Algorithmic Study: Dynamic vs. Global Routing

The core value of this project lies in the implementation and comparison of two distinct routing philosophies.

### 1. Dynamic Greedy Routing (BFS)

Implemented in `algo_dynamique.py`. This approach relies on a pre-calculated distance map using Breadth-First Search (BFS), followed by a dynamic, step-by-step simulation.

* **Mechanism:** At each simulation step, an ant evaluates its immediate neighbors. It filters out any node that mathematically increases its distance to the exit and moves to the nearest available room.
* **Performance Profile:** Highly efficient on sparse topologies containing dead ends. Because dead ends increase the BFS distance to the exit, the algorithm inherently ignores them. This local decision-making avoids costly backtracking and ensures a direct route.

### 2. Maximum Flow Modeling

Implemented in `algo_flot_max.py`. This approach treats the graph as a distribution network, drawing inspiration from Edmonds-Karp and Ford-Fulkerson algorithms.

* **Mechanism:** Before simulation begins, the algorithm pre-calculates complete end-to-end paths (using DFS/BFS augmenting paths) and assigns a maximum flow rate to each route to prevent bottlenecks.
* **Performance Profile:** Excels on complex graphs with "funnel" traps. By evaluating the global capacity of a route upfront, it prevents ants from congesting massive rooms that lead to single-capacity bottlenecks, distributing the load optimally across parallel paths.

---

## Technical Stack

* **Language:** Python 3
* **Core Libraries:**
* `NetworkX` (Graph modeling and traversal)
* `Matplotlib` (Network topology visualization)



---

## Installation and Execution

Ensure Python 3 is installed, along with the necessary dependencies:

```bash
pip install networkx matplotlib

```

The routing engines are designed as standalone executable scripts. Navigate to the root directory to run the simulations:

**Execute Dynamic Routing (BFS):**

```bash
python code/algo_dynamique.py

```

**Execute Maximum Flow Routing:**

```bash
python code/algo_flot_max.py

```

---

## Data Format and Simulation Constraints

The algorithms parse text files defining the graph topology and capacity constraints.

* `f=...` defines the total number of ants to evacuate.
* `S1 {2}` defines an intermediate room named `S1` with a maximum capacity of 2 concurrent ants.
* `Sv-S1` defines a bidirectional edge between two rooms.

The simulation outputs discrete steps, ensuring no room exceeds its capacity. Multiple ants can transition simultaneously during a single step:

```text
+++E1+++
f1-Sv-S1
f2-Sv-S2

+++E2+++
f1-S1-Sd
f2-S2-Sd
f3-Sv-S1
f4-Sv-S2

```

*(Format: `f[ant_id]-[current_room]-[next_room]`)*

```

```
