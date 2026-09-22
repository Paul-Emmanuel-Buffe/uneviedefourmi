import re
import networkx as nx


class Room:
    def __init__(self, name, capacity=1):
        self.name = name
        self.capacity = capacity
        self.ants = []


class Ant:
    def __init__(self, ant_id):
        self.id = ant_id
        self.path = None
        self.position = 0


class Anthill:

    def __init__(self):
        self.graph = nx.Graph()
        self.rooms = {}
        self.ants_count = 0

    # =====================================================
    # READ MAP
    # =====================================================

    def parse_file(self, filepath):

        with open(filepath, "r", encoding="utf-8") as file:
            lines = [
                line.strip()
                for line in file
                if line.strip()
            ]

        # Number of ants
        for line in lines:
            match = re.match(r"^f\s*=\s*(\d+)$", line)

            if match:
                self.ants_count = int(match.group(1))
                break

        # Sv and Sd have unlimited capacity
        self.rooms["Sv"] = Room("Sv", -1)
        self.rooms["Sd"] = Room("Sd", -1)

        # Rooms
        for line in lines:

            match = re.match(
                r"^(S\d+)(?:\s*\{\s*(\d+)\s*\})?$",
                line
            )

            if match:
                name = match.group(1)

                if match.group(2):
                    capacity = int(match.group(2))
                else:
                    capacity = 1

                self.rooms[name] = Room(
                    name,
                    capacity
                )

        # Tunnels
        for line in lines:

            match = re.match(
                r"^(Sv|Sd|S\d+)\s*-\s*(Sv|Sd|S\d+)$",
                line
            )

            if match:
                room1, room2 = match.groups()

                if room1 in self.rooms and room2 in self.rooms:
                    self.graph.add_edge(room1, room2)

    # =====================================================
    # FIND PATHS
    # =====================================================

    def find_paths(self):

        # Find all simple paths from Sv to Sd
        paths = list(
            nx.all_simple_paths(
                self.graph,
                source="Sv",
                target="Sd"
            )
        )

        # Shortest paths first
        paths.sort(key=len)

        # Select paths without common intermediate rooms
        selected_paths = []
        used_rooms = set()

        for path in paths:

            internal_rooms = set(path[1:-1])

            if not internal_rooms & used_rooms:

                selected_paths.append(path)
                used_rooms.update(internal_rooms)

        return selected_paths

    # =====================================================
    # ANT SIMULATION
    # =====================================================

    def simulate(self):

        paths = self.find_paths()

        if not paths:
            print("No path found.")
            return

        # Display selected paths
        print("\nSelected paths:")

        for i, path in enumerate(paths, 1):
            print(
                f"Path {i}: "
                f"{' -> '.join(path)}"
            )

        # Create ants
        ants = [
            Ant(i)
            for i in range(1, self.ants_count + 1)
        ]

        # All ants start in Sv
        self.rooms["Sv"].ants = ants.copy()

        # Assign ants to paths
        for i, ant in enumerate(ants):
            ant.path = paths[i % len(paths)]

        # Simulation
        step = 1

        while True:

            moves = []

            # Current number of ants in each room
            occupied = {
                name: len(room.ants)
                for name, room in self.rooms.items()
            }

            for ant in ants:

                # Ant has reached Sd
                if ant.position >= len(ant.path) - 1:
                    continue

                current = ant.path[ant.position]
                next_room_name = ant.path[ant.position + 1]
                next_room = self.rooms[next_room_name]

                # Check room capacity
                if (
                    next_room.capacity == -1
                    or occupied[next_room_name] < next_room.capacity
                ):

                    # Move the ant
                    self.rooms[current].ants.remove(ant)
                    next_room.ants.append(ant)

                    ant.position += 1

                    occupied[current] -= 1

                    if next_room.capacity != -1:
                        occupied[next_room_name] += 1

                    moves.append(
                        f"f{ant.id}-"
                        f"{current}-"
                        f"{next_room_name}"
                    )

            # Stop if no ant can move
            if not moves:
                break

            # Display current step
            print(f"\n+++E{step}+++")

            for move in moves:
                print(move)

            step += 1

        print(
            f"\nEvacuation completed in "
            f"{step - 1} steps."
        )