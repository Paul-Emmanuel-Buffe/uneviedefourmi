"""Maximum flow routing based on Edmonds-Karp/Ford-Fulkerson concepts."""

import networkx as nx
from classes_ants import charger_fourmilieres

def _chemin_bfs(H, source, target):
    """Edmonds-Karp: Shortest augmenting path (BFS)."""
    try:
        return nx.shortest_path(H, source=source, target=target)
    except nx.NetworkXNoPath:
        return None

def _chemin_dfs(H, source, target):
    """Generic Ford-Fulkerson: First augmenting path found (DFS)."""
    pile = [(source, [source])]
    vus = {source}
    while pile:
        noeud, chemin = pile.pop()
        if noeud == target:
            return chemin
        for suivant in H.successors(noeud):
            if suivant not in vus:
                vus.add(suivant)
                pile.append((suivant, chemin + [suivant]))
    return None

_CHERCHEURS_DE_CHEMIN = {"bfs": _chemin_bfs, "dfs": _chemin_dfs}

def graphe_de_flot(G):
    """Builds a flow graph by splitting nodes to handle room capacities."""
    H = nx.DiGraph()
    for salle in G.nodes:
        if salle not in ("Sv", "Sd"):
            capacite = G.nodes[salle].get("capacite", 1)
            H.add_edge(f"{salle}_in", f"{salle}_out", capacity=capacite)

    def entree(s):
        return s if s in ("Sv", "Sd") else f"{s}_in"

    def sortie(s):
        return s if s in ("Sv", "Sd") else f"{s}_out"

    for a, b in G.edges:
        H.add_edge(sortie(a), entree(b), capacity=float("inf"))
        H.add_edge(sortie(b), entree(a), capacity=float("inf"))

    return H

def vers_chemin_salles(chemin_h):
    """Merges in/out flow nodes back into standard room names."""
    salles = [noeud.replace("_in", "").replace("_out", "") for noeud in chemin_h]
    chemin_salles = [salles[0]]
    for s in salles[1:]:
        if s != chemin_salles[-1]:
            chemin_salles.append(s)
    return chemin_salles

def trouver_chemins(G, methode="dfs", max_chemins=None):
    """Decomposes the graph into multiple parallel paths from start to end."""
    H = graphe_de_flot(G)
    chercher_chemin = _CHERCHEURS_DE_CHEMIN[methode]

    chemins = []
    while max_chemins is None or len(chemins) < max_chemins:
        chemin_h = chercher_chemin(H, "Sv", "Sd")
        if chemin_h is None:
            break

        capacite_min = min(H[u][v]["capacity"] for u, v in zip(chemin_h, chemin_h[1:]))
        chemins.append(vers_chemin_salles(chemin_h))

        # Direct path absorbs all flow
        if capacite_min == float("inf"):
            break

        # Consume 1 unit of capacity along the found path
        for u, v in zip(chemin_h, chemin_h[1:]):
            H[u][v]["capacity"] -= 1
            if H[u][v]["capacity"] <= 0:
                H.remove_edge(u, v)

    return chemins

def assigner_chemins(chemins, nb_fourmis):
    """Assigns the optimal path to each ant based on current load."""
    compteurs = [0] * len(chemins)
    affectations = []
    for _ in range(nb_fourmis):
        arrivees = [len(chemins[i]) - 1 + compteurs[i] for i in range(len(chemins))]
        i = arrivees.index(min(arrivees))
        affectations.append(i)
        compteurs[i] += 1
    return affectations

def simuler_chemins(chemins, G, nb_fourmis, affichage=True):
    """Simulates movements along pre-calculated paths."""
    if not chemins:
        raise ValueError("No valid path between Sv and Sd.")

    affectations = assigner_chemins(chemins, nb_fourmis)
    chemin_de = [chemins[i] for i in affectations] 

    capacites = {s: G.nodes[s].get("capacite", 1) for s in G.nodes}
    positions = [0] * nb_fourmis          
    occupation = {}                       

    def est_arrivee(i):
        return chemin_de[i][positions[i]] == "Sd"

    etape = 0
    while not all(est_arrivee(i) for i in range(nb_fourmis)):
        etape += 1

        # Move ants closest to the exit first to free up rooms behind them
        ordre = sorted(range(nb_fourmis), key=lambda i: -positions[i])

        for i in ordre:
            if est_arrivee(i):
                continue

            salle_actuelle = chemin_de[i][positions[i]]
            salle_suivante = chemin_de[i][positions[i] + 1]

            place_libre = (
                salle_suivante in ("Sv", "Sd")
                or occupation.get(salle_suivante, 0) < capacites[salle_suivante]
            )

            if place_libre:
                if salle_actuelle not in ("Sv", "Sd"):
                    occupation[salle_actuelle] -= 1
                positions[i] += 1
                if salle_suivante not in ("Sv", "Sd"):
                    occupation[salle_suivante] = occupation.get(salle_suivante, 0) + 1

        if affichage:
            print(f"Step {etape} :", [chemin_de[i][positions[i]] for i in range(nb_fourmis)])

    if affichage:
        print(f"\nAll ants arrived in {etape} steps.")
    return etape

def simuler(G, nb_fourmis, methode="dfs", max_chemins=None, affichage=True):
    """Default entry point triggering pathfinding then simulation."""
    chemins = trouver_chemins(G, methode=methode, max_chemins=max_chemins)
    return simuler_chemins(chemins, G, nb_fourmis, affichage=affichage)

def resoudre_fourmiliere(fourmiliere, **options):
    """Wrapper to resolve a generic Fourmiliere object."""
    G = fourmiliere.vers_graphe()
    if options.get("affichage", True):
        print(f"\n=== {fourmiliere.nom} ({fourmiliere.nb_fourmis} ants) ===")
    return simuler(G, fourmiliere.nb_fourmis, **options)

if __name__ == "__main__":
    # Standalone execution entry point
    from pathlib import Path
    
    # Load all maps and execute the max flow algorithm
    data_path = Path(__file__).parent / "data"
    if data_path.exists():
        fourmilieres = charger_fourmilieres(data_path)
        for name, colony in fourmilieres.items():
            resoudre_fourmiliere(colony, methode="bfs")
    else:
        print("Please create a 'data' folder containing your .txt files.")