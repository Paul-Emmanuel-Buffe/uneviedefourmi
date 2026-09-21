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
            self.adjacency[room] = []
            
            if room == self.start_room or room == self.end_room:
                self.capacities[room] = float("inf")
            else:
                self.capacities[room] = 1

    def add_tunnel(self, a, b):
        self.init_room(a)
        self.init_room(b)
        self.adjacency[a].append(b)
        self.adjacency[b].append(a)

    def calculate_distances(self):
        distances = {self.end_room: 0}
        to_visit = [self.end_room] 
        
        while len(to_visit) > 0:
            room = to_visit.pop(0)
            
            for neighbor in self.adjacency.get(room, []):
                if neighbor not in distances:
                    distances[neighbor] = distances[room] + 1
                    to_visit.append(neighbor)
                    
        if self.start_room in distances:
            return distances
        else:
            return None

    @classmethod 
    def from_file(cls, file_path):
        colony = cls()
        
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            
        for line in lines:
            line = line.strip()
            if line == "":
                continue 
                
            if line.lower().startswith("f") and "=" in line:
                parts = line.split("=")
                colony.num_ants = int(parts[1].strip())
                
            elif " - " in line:
                parts = line.split(" - ")
                colony.add_tunnel(parts[0].strip(), parts[1].strip())
                
            elif "{" in line:
                parts = line.split("{")
                name = parts[0].strip()
                cap = parts[1].replace("}", "").strip()
                colony.init_room(name)
                colony.capacities[name] = int(cap)
                
            else:
                colony.init_room(line)

        if colony.num_ants is None:
            raise ValueError("Nombre de fourmis manquant.")
            
        return colony

    def simulate(self, distances):
        ants = {}
        for i in range(1, self.num_ants + 1):
            ants[i] = self.start_room
            
        step = 1
        
        while len(ants) > 0:
            moves = []
            occupancy = {}
            for room in self.adjacency:
                occupancy[room] = 0
            
            for ant_id, current_room in list(ants.items()):
                neighbors = []
                for n in self.adjacency[current_room]:
                    if n in distances and distances[n] < distances.get(current_room, float('inf')):
                        neighbors.append(n)
                        
                neighbors.sort(key=lambda n: distances[n])
                
                has_moved = False
                for neighbor in neighbors:
                    cap_max = self.capacities.get(neighbor, 1)
                    
                    if occupancy[neighbor] < cap_max:
                        ants[ant_id] = neighbor
                        occupancy[neighbor] += 1
                        moves.append(f"f{ant_id}-{current_room}-{neighbor}")
                        has_moved = True
                        
                        if neighbor == self.end_room:
                            del ants[ant_id]
                        break
                        
                if has_moved == False:
                    occupancy[current_room] += 1
            
            if len(moves) > 0:
                print(f"+++E{step}+++")
                for move in moves:
                    print(move)
                step += 1



    def display_graph(self):
        G = nx.Graph(self.adjacency)
        colors = ["lightgreen" if n == self.start_room else "salmon" if n == self.end_room else "lightblue" for n in G.nodes()]
        
        plt.figure(figsize=(15, 11))
        nx.draw(G, with_labels=True, node_color=colors, node_size=1500, font_weight="bold", edge_color="gray")
        plt.title(f"Réseau de la Fourmilière ({self.num_ants} fourmis)")
        plt.show()

    def __repr__(self):
        return f"AntColony(Fourmis={self.num_ants}, Salles={len(self.adjacency)})"