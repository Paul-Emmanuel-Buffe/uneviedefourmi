import networkx as nx

#GYM1 la liste d'arretes
edges=[("Sv", "S1"), ("Sv", "S2"), ("S1", "Sd"), ("S2", "Sd")]

#GM2 construction du graphe
G = nx.Graph()
G.add_edges_from(edges)

# GMA3 TROUVER LES VOISINS D4UNE SALLE
voisins_s1=list(G.neighbors("S1"))

#GYM4 parcours en largeur
chemin = nx.shortest_path(G, source="Sv", target="Sd")


# ---------------------------------------------------------------------------
# GYM5+ :  On cherche maintenant TOUS les
# chemins Sv -> Sd utilisables en parallèle, puis on y répartit les fourmis.
# ---------------------------------------------------------------------------

def _chemin_bfs(H, source, target):
    """Edmonds-Karp : le chemin augmentant le plus court (en nombre d'arêtes)."""
    try:
        return nx.shortest_path(H, source=source, target=target)
    except nx.NetworkXNoPath:
        return None


def _chemin_dfs(H, source, target):
    """Ford-Fulkerson générique : le premier chemin augmentant trouvé, pas
    forcément le plus court -> sert de comparaison pour le benchmark."""
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
    """Construit le graphe de flot : chaque salle {capacité c} devient
    salle_in -> salle_out (capacité c), Sv/Sd restent illimités et ne sont
    pas dédoublés. Réutilisé par tous les algos basés sur le flot maximum."""
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
    """Convertit un chemin du graphe de flot (avec _in/_out) en chemin de
    salles (Sv, S1, ..., Sd), en fusionnant les paires salle_in/salle_out."""
    salles = [noeud.replace("_in", "").replace("_out", "") for noeud in chemin_h]
    chemin_salles = [salles[0]]
    for s in salles[1:]:
        if s != chemin_salles[-1]:
            chemin_salles.append(s)
    return chemin_salles


def trouver_chemins(G, methode="dfs", max_chemins=None):
    """Décompose la fourmilière en plusieurs chemins Sv -> Sd, chacun utilisable
    par une fourmi à la fois. Une salle de capacité c apparaît dans c chemins
    différents (donc c fourmis peuvent y être en même temps, une par chemin).

    methode : "bfs" (Edmonds-Karp, chemins augmentants les plus courts) ou
    "dfs" (Ford-Fulkerson générique, chemins augmentants quelconques).
    max_chemins : arrête la recherche après ce nombre de chemins (None = sans
    limite, jusqu'à épuisement des capacités). max_chemins=1 donne la version
    "naïve" à un seul chemin (tout le monde en file indienne)."""

    H = graphe_de_flot(G)
    chercher_chemin = _CHERCHEURS_DE_CHEMIN[methode]

    chemins = []
    while max_chemins is None or len(chemins) < max_chemins:
        chemin_h = chercher_chemin(H, "Sv", "Sd")
        if chemin_h is None:
            break

        capacite_min = min(H[u][v]["capacity"] for u, v in zip(chemin_h, chemin_h[1:]))
        chemins.append(vers_chemin_salles(chemin_h))

        if capacite_min == float("inf"):
            # un tunnel relie directement Sv à Sd (aucune salle entre les deux,
            # donc aucune capacité à épuiser) : ce chemin absorbe déjà toutes
            # les fourmis à lui seul, inutile de chercher plus loin
            break

        # on retire 1 unité de capacité le long de ce chemin. Version simplifiée
        # d'Edmonds-Karp : on n'ajoute pas d'arêtes inverses, donc on ne peut
        # pas annuler un chemin déjà retenu (le vrai algorithme le peut)
        for u, v in zip(chemin_h, chemin_h[1:]):
            H[u][v]["capacity"] -= 1
            if H[u][v]["capacity"] <= 0:
                H.remove_edge(u, v)

    return chemins


def assigner_chemins(chemins, nb_fourmis):
    """Associe à chaque fourmi le chemin qui la fera arriver le plus tôt.
    Sur un chemin de L tunnels, une fourmi entre par étape : la (k+1)-ième
    fourmi envoyée sur ce chemin arrive à l'étape L + k."""
    compteurs = [0] * len(chemins)
    affectations = []
    for _ in range(nb_fourmis):
        arrivees = [len(chemins[i]) - 1 + compteurs[i] for i in range(len(chemins))]
        i = arrivees.index(min(arrivees))
        affectations.append(i)
        compteurs[i] += 1
    return affectations


def simuler_chemins(chemins, G, nb_fourmis, affichage=True):
    """Simule le déplacement des fourmis étant donné un ensemble de chemins
    Sv -> Sd déjà calculé (par n'importe quel algo). Commun à toutes les
    stratégies "planifiées à l'avance" du benchmark."""
    if not chemins:
        raise ValueError("Aucun chemin entre Sv et Sd.")

    affectations = assigner_chemins(chemins, nb_fourmis)
    chemin_de = [chemins[i] for i in affectations]  # chemin_de[i] = chemin de la fourmi i

    capacites = {s: G.nodes[s].get("capacite", 1) for s in G.nodes}
    positions = [0] * nb_fourmis          # index de chaque fourmi dans SON chemin
    occupation = {}                       # salle -> nombre de fourmis dedans

    def est_arrivee(i):
        return chemin_de[i][positions[i]] == "Sd"

    etape = 0
    while not all(est_arrivee(i) for i in range(nb_fourmis)):
        etape += 1

        # on avance en priorité les fourmis les plus proches du dortoir, pour
        # qu'une salle se libère avant que la fourmi suivante n'y entre
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
            print(f"etape {etape} :", [chemin_de[i][positions[i]] for i in range(nb_fourmis)])

    if affichage:
        print(f"\nToutes les fourmis sont arrivees en {etape} etapes.")
    return etape


def simuler(G, nb_fourmis, methode="dfs", max_chemins=None, affichage=True):
    """Stratégie par défaut : chemins trouvés via trouver_chemins (BFS/DFS
    sur le graphe de flot), puis simulés avec simuler_chemins."""
    chemins = trouver_chemins(G, methode=methode, max_chemins=max_chemins)
    return simuler_chemins(chemins, G, nb_fourmis, affichage=affichage)


def resoudre_fourmiliere(fourmiliere, **options):
    """Point d'entrée générique : on lui donne une Fourmiliere (ants.py,
    chargée depuis un fichier ou construite à la main) et elle en extrait
    elle-même les salles et les tunnels via vers_graphe(), avant de simuler.
    Les options (methode, max_chemins, affichage) sont transmises à simuler()."""
    G = fourmiliere.vers_graphe()
    if options.get("affichage", True):
        print(f"\n=== {fourmiliere.nom} ({fourmiliere.nb_fourmis} fourmis) ===")
    return simuler(G, fourmiliere.nb_fourmis, **options)


# GYM 6 : attention à la complexité
# - trouver_chemins : chaque itération cherche un chemin (O(V+E)) et retire au
#   moins 1 unité de capacité ; il y a donc au plus (somme des capacités)
#   itérations, que ce soit en BFS (Edmonds-Karp, polynomial garanti) ou en
#   DFS (Ford-Fulkerson générique, mêmes garanties ici car capacités entières).
#   La méthode ne change PAS le nombre d'itérations, mais change LA LONGUEUR
#   des chemins trouvés -> impact direct sur le nombre d'étapes final, d'où
#   l'intérêt de comparer les deux (voir benchmark.py).
# - assigner_chemins : nb_fourmis itérations, chacune O(nb_chemins) -> négligeable.
# - simuler : au pire nb_fourmis + longueur_max étapes, chacune O(nb_fourmis)
#   -> reste largement raisonnable pour les tailles de fourmilière du sujet.

if __name__ == "__main__":
    # démo GYM1 : graphe fait à la main
    print("Voisins de S1 :", voisins_s1)
    print("Chemin le plus court Sv -> Sd :", chemin)
    print("Chemins disponibles :", trouver_chemins(G))
    print()
    simuler(G, nb_fourmis=5)

    # démo modulaire : on donne directement des Fourmiliere chargées depuis
    # des fichiers, resoudre_fourmiliere() se charge d'en extraire le graphe
    from pathlib import Path
    from classes_ants import charger_fourmilieres

    fourmilieres = charger_fourmilieres(Path(__file__).parent / "Data")
    for fourmiliere in fourmilieres.values():
        resoudre_fourmiliere(fourmiliere)
