"""Modélisation orientée objet des fourmilières."""

import re
from pathlib import Path

import networkx as nx


class Salle:
    """Une salle de la fourmilière (vestibule et dortoir inclus)."""

    def __init__(self, nom, capacite=1):
        self.nom = nom
        self.capacite = capacite
        self.occupants = []  # rempli pendant la simulation des déplacements

    def est_libre(self):
        return len(self.occupants) < self.capacite

    def __repr__(self):
        cap = "inf" if self.capacite == float("inf") else self.capacite
        return f"Salle({self.nom!r}, capacite={cap})"


class Fourmiliere:
    """Un graphe de salles reliées par des tunnels, avec un nombre de fourmis à déplacer."""

    def __init__(self, nb_fourmis, nom="fourmiliere"):
        self.nom = nom
        self.nb_fourmis = nb_fourmis
        self.salles = {}
        self.tunnels = []
        self._ajouter_salle("Sv", capacite=float("inf"))
        self._ajouter_salle("Sd", capacite=float("inf"))

    def _ajouter_salle(self, nom, capacite=1):
        if nom not in self.salles:
            self.salles[nom] = Salle(nom, capacite)
        return self.salles[nom]

    def ajouter_tunnel(self, a, b):
        self._ajouter_salle(a)
        self._ajouter_salle(b)
        self.tunnels.append((a, b))

    def voisins(self, nom):
        return [b for a, b in self.tunnels if a == nom] + [a for a, b in self.tunnels if b == nom]

    def vers_graphe(self):
        """Construit le graphe NetworkX correspondant (nœuds annotés par leur capacité)."""
        G = nx.Graph()
        for nom, salle in self.salles.items():
            G.add_node(nom, capacite=salle.capacite)
        G.add_edges_from(self.tunnels)
        return G

    def __repr__(self):
        return (
            f"Fourmiliere({self.nom!r}, fourmis={self.nb_fourmis}, "
            f"salles={len(self.salles)}, tunnels={len(self.tunnels)})"
        )

    def afficher(self):
        """Affiche la fourmilière dans le terminal, salles regroupées par distance
        (en tunnels) au vestibule : on voit ainsi le flux Sv -> ... -> Sd."""
        G = self.vers_graphe()
        distances = nx.single_source_shortest_path_length(G, "Sv")

        couches = {}
        for nom, d in distances.items():
            couches.setdefault(d, []).append(nom)

        titre = f"{self.nom} - {self.nb_fourmis} fourmis, {len(self.salles)} salles, {len(self.tunnels)} tunnels"
        print(titre)
        print("-" * len(titre))
        for d in sorted(couches):
            def etiquette(nom):
                cap = self.salles[nom].capacite
                cap = "inf" if cap == float("inf") else cap
                return f"{nom}({cap})"

            ligne = "  ".join(etiquette(nom) for nom in sorted(couches[d]))
            print(f"  distance {d} : {ligne}")
        print("  tunnels :", ", ".join(f"{a}-{b}" for a, b in self.tunnels))
        print()


_RE_NB_FOURMIS = re.compile(r"^[fF]\s*=\s*(\d+)$")
_RE_TUNNEL = re.compile(r"^(\S+)\s*-\s*(\S+)$")
_RE_SALLE = re.compile(r"^(\S+?)(?:\s*\{\s*(\d+)\s*\})?$")


def parser_fourmiliere(chemin):
    """Charge une fourmilière depuis un fichier texte (une fourmilière par fichier)."""
    chemin = Path(chemin)
    lignes = [
        ligne.strip()
        for ligne in chemin.read_text(encoding="utf-8").splitlines()
        if ligne.strip()
    ]

    m_fourmis = _RE_NB_FOURMIS.match(lignes[0])
    if not m_fourmis:
        raise ValueError(f"{chemin.name}: première ligne invalide ({lignes[0]!r}), attendu 'f=<N>'")
    fourmiliere = Fourmiliere(int(m_fourmis.group(1)), nom=chemin.stem)

    declarations, tunnels = [], []
    for ligne in lignes[1:]:
        m_tunnel = _RE_TUNNEL.match(ligne)
        if m_tunnel:
            tunnels.append(m_tunnel.groups())
        else:
            declarations.append(ligne)

    for ligne in declarations:
        m_salle = _RE_SALLE.match(ligne)
        if not m_salle:
            raise ValueError(f"{chemin.name}: ligne de salle invalide ({ligne!r})")
        nom, capacite = m_salle.groups()
        fourmiliere._ajouter_salle(nom, int(capacite) if capacite else 1)

    for a, b in tunnels:
        fourmiliere.ajouter_tunnel(a, b)

    return fourmiliere


def charger_fourmilieres(dossier):
    """Charge toutes les fourmilières (*.txt) d'un dossier. Renvoie {nom_fichier: Fourmiliere}."""
    dossier = Path(dossier)
    return {
        chemin.stem: parser_fourmiliere(chemin)
        for chemin in sorted(dossier.glob("*.txt"))
    }


if __name__ == "__main__":
    fourmilieres = charger_fourmilieres(Path(__file__).parent / "Data")
    for fourmiliere in fourmilieres.values():
        fourmiliere.afficher()
