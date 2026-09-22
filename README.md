# Une Vie de Fourmi

A Python project that simulates the evacuation of ants through a network of rooms and tunnels.

The goal is to move all ants from the entrance room `Sv` to the destination room `Sd`, while respecting the capacity of each room.

---

## Project Overview

The anthill is represented as a graph:

* **Rooms** are graph vertices.
* **Tunnels** are graph edges.
* `Sv` is the starting room.
* `Sd` is the destination room.
* Intermediate rooms have a limited capacity.
* Ants move step by step until they reach `Sd`.

The project uses **NetworkX** to represent the graph and find possible paths.

---

## Path Finding Algorithm

The personal version of the project uses:

```python
nx.all_simple_paths()
```

This function finds all **simple paths** between `Sv` and `Sd`.

A simple path is a path where a room is not visited more than once.

### Path selection

After finding all possible paths:

1. The paths are sorted by length.
2. The shortest paths are considered first.
3. A path is selected if it does not share an intermediate room with an already selected path.
4. This continues until no more compatible paths can be selected.

For example:

```text
Sv → S1 → Sd
Sv → S2 → Sd
Sv → S1 → S3 → Sd
```

The first two paths can be selected because they do not share an intermediate room.

The third path is not selected because it uses `S1`, which is already used by another path.

### Important note

`all_simple_paths()` can become expensive on large or highly connected graphs because the number of possible simple paths can be very large.

The path selection is also **greedy**, so it does not guarantee the mathematically optimal combination of paths.

---

## Ant Simulation

Once the paths have been selected, the ants are assigned to them.

The simulation works with discrete steps:

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

At each step:

* An ant tries to move to the next room on its path.
* The destination room capacity is checked.
* If the room is full, the ant waits.
* Several ants can move during the same step.
* `Sv` and `Sd` have unlimited capacity.

The simulation ends when every ant has reached `Sd`.

---

## Room Capacities

Rooms can have different capacities.

Example:

```text
S1
S2 {2}
S3 {3}
```

This means:

| Room |  Capacity |
| ---- | --------: |
| `Sv` | Unlimited |
| `Sd` | Unlimited |
| `S1` |         1 |
| `S2` |         2 |
| `S3` |         3 |

If a room has capacity `1`, only one ant can occupy it at a time.

---

## Project Structure

```text
Une_Vie_de_Fourmi/
│
├── ants.py
├── main.py
├── visualisation.py
│
├── maps/
│   ├── fourmiliere_un.txt
│   ├── fourmiliere_deux.txt
│   ├── fourmiliere_trois.txt
│   ├── fourmiliere_quatre.txt
│   └── fourmiliere_cinq.txt
│
├── Viz_graphe/
│   └── ...
│
└── README.md
```

### Main files

#### `ants.py`

Contains the main classes and the simulation:

* `Room`
* `Ant`
* `Anthill`

It handles:

* Map parsing
* Graph creation
* Path finding
* Path selection
* Ant creation
* Ant movement
* Room capacities
* Evacuation simulation

#### `main.py`

The main entry point of the program.

It loads a map and starts the simulation.

#### `visualisation.py`

Creates a graphical representation of the anthill using:

* NetworkX
* Matplotlib

The generated graph is saved as a PNG file in:

```text
Viz_graphe/
```

---

## Map Format

A map contains the number of ants, rooms, and tunnels.

Example:

```text
f = 4

Sv
Sd

S1
S2

Sv-S1
Sv-S2
S1-Sd
S2-Sd
```

A room can also have a specific capacity:

```text
S1 {2}
```

This means that `S1` can contain two ants at the same time.

---

##  Running the Simulation

Make sure Python is installed.

Install the required libraries:

```bash
pip install networkx matplotlib
```

Then run:

```bash
python main.py
```

The program will read:

```text
maps/fourmiliere_un.txt
```

and start the evacuation simulation.

---

## Graph Visualization

To generate the graph visualization:

```bash
python visualisation.py
```

You can also specify another map:

```bash
python visualisation.py maps/fourmiliere_cinq.txt
```

The PNG file will be saved automatically in:

```text
Viz_graphe/
```

For example:

```text
Viz_graphe/topologie_fourmiliere_cinq.png
```

### Visualization

The graph uses different colors to distinguish the main rooms:

* 🟢 `Sv` → starting room
* 🔴 `Sd` → destination room
* 🔵 Other rooms → intermediate rooms

The capacity of each room is also displayed.

---

## Program Workflow

The complete workflow is:

```text
Read the map
     ↓
Create the graph
     ↓
Find all simple paths
     ↓
Sort paths by length
     ↓
Select compatible paths
     ↓
Create the ants
     ↓
Assign ants to paths
     ↓
Simulate movements
     ↓
Check room capacities
     ↓
Repeat until all ants reach Sd
```

---

## Example

Suppose the map contains:

```text
f = 4

Sv
Sd

S1
S2

Sv-S1
Sv-S2
S1-Sd
S2-Sd
```

The program can find these paths:

```text
Sv → S1 → Sd
Sv → S2 → Sd
```

The ants are distributed between these paths.

The simulation can then produce:

```text
+++E1+++
f1-Sv-S1
f2-Sv-S2

+++E2+++
f1-S1-Sd
f2-S2-Sd
f3-Sv-S1
f4-Sv-S2

+++E3+++
f3-S1-Sd
f4-S2-Sd
```

Finally:

```text
Evacuation completed in 3 steps.
```

---

## Project Objectives

This project demonstrates several programming concepts:

* Graph representation
* Graph traversal
* Path finding
* Object-oriented programming
* File parsing
* Simulation
* Capacity management
* Step-by-step movement
* Graph visualization

The project also shows how a graph algorithm can be combined with a simulation system.

---

## Limitations

The current implementation is intentionally simple.

`all_simple_paths()` searches for all simple paths, which can become expensive for large graphs.

The path selection is greedy:

* Paths are sorted by length.
* Compatible paths are selected one by one.
* The algorithm does not guarantee the optimal global solution.

The goal of this version is to keep the implementation understandable while demonstrating graph algorithms and ant movement simulation.

---

## Technologies

* **Python 3**
* **NetworkX**
* **Matplotlib**
* **Git / GitHub**

---

## Personal Contribution

My implementation focuses on:

* Finding paths with `NetworkX.all_simple_paths()`
* Sorting paths by length
* Selecting paths without shared intermediate rooms
* Simulating ant movement step by step
* Managing room capacities
* Visualizing the graph
* Exporting graph visualizations as PNG files

The implementation was designed to remain simple and easy to understand.
