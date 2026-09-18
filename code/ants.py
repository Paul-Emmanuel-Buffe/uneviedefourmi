import networkx as nx
import matplotlib.pyplot as plt

class AntColony:
    def __init__(self, start_room="Sv", end_room="Sd"):
        self.adjacency = {}
        self.capacities = {}
        self.start_room = start_room
        self.end_room = end_room
        self.num_ants = None

    def init_room(self, room):
        if room not in self.adjacency:
            self.adjacency[room] = set()
            self.capacities[room] = float("inf") if room in (self.start_room, self.end_room) else 1

    def add_tunnel(self, a, b):
        self.init_room(a)
        self.init_room(b)
        self.adjacency[a].add(b)
        self.adjacency[b].add(a)

    def calculate_distances(self):
        distances = {self.end_room: 0}
        to_visit = [self.end_room]
        
        while to_visit:
            room = to_visit.pop(0)
            for neighbor in self.adjacency.get(room, []):
                if neighbor not in distances:
                    distances[neighbor] = distances[room] + 1
                    to_visit.append(neighbor)
                    
        return distances if self.start_room in distances else None

    @classmethod 
    def from_file(cls, file_path):
        colony = cls()
        with open(file_path, encoding="utf-8") as file:
            for line in (l.strip() for l in file if l.strip()):
                if line.lower().startswith("f") and "=" in line:
                    colony.num_ants = int(line.split("=")[1].strip())
                elif " - " in line:
                    a, b = line.split(" - ")
                    colony.add_tunnel(a.strip(), b.strip())
                elif "{" in line:
                    name, cap = line.replace("}", "").split("{")
                    colony.init_room(name.strip())
                    colony.capacities[name.strip()] = int(cap.strip())
                else:
                    colony.init_room(line)

        if not colony.num_ants:
            raise ValueError("Nombre de fourmis manquant.")
        return colony

    def simulate(self, distances):
        ants = {i: self.start_room for i in range(1, self.num_ants + 1)}
        step = 1
        
        while ants:
            moves = []
            occupancy = {room: 0 for room in self.adjacency}
            
            for ant_id, current_room in list(ants.items()):
                neighbors = [n for n in self.adjacency[current_room] if distances.get(n, float('inf')) < distances[current_room]]
                neighbors.sort(key=lambda n: distances[n])
                
                has_moved = False
                for neighbor in neighbors:
                    if occupancy[neighbor] < self.capacities.get(neighbor, 1):
                        ants[ant_id] = neighbor
                        occupancy[neighbor] += 1
                        moves.append(f"f{ant_id}-{current_room}-{neighbor}")
                        has_moved = True
                        
                        if neighbor == self.end_room:
                            del ants[ant_id]
                        break
                        
                if not has_moved:
                    occupancy[current_room] += 1
            
            if moves:
                print(f"+++E{step}+++")
                print("\n".join(moves))
                step += 1

    def display_graph(self):
        G = nx.Graph(self.adjacency)
        colors = ["lightgreen" if n == self.start_room else "salmon" if n == self.end_room else "lightblue" for n in G.nodes()]
        
        plt.figure(figsize=(15, 11))
        nx.draw(G, with_labels=True, node_color=colors, node_size=1500, font_weight="bold", edge_color="gray")
        plt.title(f"Réseau de la Fourmilière ({self.num_ants} fourmis)")
        plt.show()

    def __repr__(self):
        return f"AntColony(Fourmis={self.num_ants}, Salles={len(self.adjacency)}, valide={bool(self.calculate_distances())})"