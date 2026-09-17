import networkx as nx
import matplotlib.pyplot as plt

class Fourmiliere:
    CAPACITE_PAR_DEFAUT = 1
    CAPACITE_ILLIMITE = float("inf")

    def __init__(self, vestibule="Sv", dortoir="Sd"):
        self.adjacence = {}
        self.capacites = {}
        self.vestibule = vestibule
        self.dortoir = dortoir
        self.nb_fourmis = None

    def ajouter_salle(self, nom_salle):
        if nom_salle not in self.adjacence:
            self.adjacence[nom_salle] = set()
            self.capacites[nom_salle] = self.CAPACITE_ILLIMITE if nom_salle in (self.vestibule, self.dortoir) else self.CAPACITE_PAR_DEFAUT

    def ajouter_tunnel(self, salle_a, salle_b):
        self.ajouter_salle(salle_a)
        self.ajouter_salle(salle_b)
        self.adjacence[salle_a].add(salle_b)
        self.adjacence[salle_b].add(salle_a)

    def definir_capacite(self, salle, capacite):
        self.ajouter_salle(salle)
        self.capacites[salle] = capacite

    def trouver_chemin(self):
        a_visiter = [[self.vestibule]] 
        visites = {self.vestibule}
        
        while a_visiter:
            chemin = a_visiter.pop(0)
            salle_actuelle = chemin[-1]
            
            if salle_actuelle == self.dortoir:
                return chemin
                
            for voisin in self.adjacence.get(salle_actuelle, set()):
                if voisin not in visites:
                    visites.add(voisin)
                    a_visiter.append(chemin + [voisin])
                    
        return None

    @classmethod 
    def depuis_fichier(cls, chemin_fichier):
        colonie = cls()
        with open(chemin_fichier, encoding="utf-8") as fichier:
            for ligne in (l.strip() for l in fichier if l.strip()):
                if ligne.lower().startswith("f") and "=" in ligne:
                    colonie.nb_fourmis = int(ligne.split("=")[1].strip())
                elif " - " in ligne:
                    a, b = (s.strip() for s in ligne.split(" - "))
                    colonie.ajouter_tunnel(a, b)
                elif "{" in ligne:
                    nom, reste = ligne.split("{", 1)
                    colonie.definir_capacite(nom.strip(), int(reste.replace("}", "").strip()))
                else:
                    colonie.ajouter_salle(ligne)

        if colonie.nb_fourmis is None:
            raise ValueError(f"Nombre de fourmis manquant dans {chemin_fichier}")
        return colonie

    def simuler(self, chemin):
        fourmis = {i: 0 for i in range(1, self.nb_fourmis + 1)}
        etape = 1
        
        while fourmis:
            mouvements = []
            occupations = {salle: 0 for salle in chemin}
            
            for f_id in list(fourmis.keys()):
                idx = fourmis[f_id]
                salle, suivante = chemin[idx], chemin[idx + 1]
                
                if occupations[suivante] < self.capacites.get(suivante, self.CAPACITE_PAR_DEFAUT):
                    fourmis[f_id] += 1
                    occupations[suivante] += 1
                    mouvements.append(f"f{f_id}-{salle}-{suivante}")
                    
                    if suivante == self.dortoir:
                        del fourmis[f_id]
                else:
                    occupations[salle] += 1
            
            if mouvements:
                print(f"+++E{etape}+++")
                print("\n".join(mouvements))
                etape += 1

    def afficher_graphe(self):
        G = nx.Graph()
        
        for salle, voisins in self.adjacence.items():
            for voisin in voisins:
                G.add_edge(salle, voisin)
                
        couleurs = []
        for noeud in G.nodes():
            if noeud == self.vestibule:
                couleurs.append("lightgreen")
            elif noeud == self.dortoir:
                couleurs.append("salmon")
            else:
                couleurs.append("lightblue")
                
        plt.figure(figsize=(10, 7))
        nx.draw(G, with_labels=True, node_color=couleurs, node_size=1500, font_weight="bold", edge_color="gray")
        plt.title(f"Réseau de la Fourmilière ({self.nb_fourmis} fourmis)")
        plt.show()

    def __repr__(self):
        return f"Fourmiliere(F={self.nb_fourmis}, Salles={len(self.adjacence)}, valide={bool(self.trouver_chemin())})"