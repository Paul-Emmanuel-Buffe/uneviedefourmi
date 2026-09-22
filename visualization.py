import os
import sys

import matplotlib.pyplot as plt
import networkx as nx

from ants import Anthill


def display_topology(filepath):

    # Read the map
    anthill = Anthill()
    anthill.parse_file(filepath)

    graph = anthill.graph

    # Create output folder
    os.makedirs("Viz_graphe", exist_ok=True)

    # Position of the rooms
    pos = nx.spring_layout(
        graph,
        seed=42
    )

    # Room colors
    colors = []

    for node in graph.nodes():

        if node == "Sv":
            colors.append("#2ecc71")

        elif node == "Sd":
            colors.append("#e74c3c")

        else:
            colors.append("#3498db")

    # Room labels
    labels = {}

    for node in graph.nodes():

        room = anthill.rooms[node]

        if room.capacity == -1:
            labels[node] = f"{node}\n∞"
        else:
            labels[node] = (
                f"{node}\n"
                f"{{{room.capacity}}}"
            )

    # Draw rooms
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=colors,
        node_size=1200
    )

    # Draw tunnels
    nx.draw_networkx_edges(
        graph,
        pos,
        width=2
    )

    # Draw labels
    nx.draw_networkx_labels(
        graph,
        pos,
        labels=labels,
        font_color="white",
        font_weight="bold"
    )

    # Title
    filename = os.path.basename(filepath)

    plt.title(
        f"Topology: {filename}"
    )

    plt.axis("off")
    plt.tight_layout()

    # PNG file name
    name = os.path.splitext(filename)[0]

    output = os.path.join(
        "Viz_graphe",
        f"topology_{name}.png"
    )

    # Save image
    plt.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )

    print(
        f"Visualization saved: {output}"
    )

    plt.show()
    plt.close()


if __name__ == "__main__":

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "maps/fourmiliere_un.txt"

    display_topology(filepath)