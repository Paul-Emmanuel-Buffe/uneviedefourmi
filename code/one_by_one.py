import networkx as nx
import matplotlib.pyplot as plt

class Fourmiliere:
    def __init__(self, vestibule="Sv", dortoir="Sd"):
        self.adjacence = {}
        self.capacites = {}
        self.vestibule = vestibule
        self.dortoir = dortoir
        self.nb_fourmis = None

    def init_salle(self, salle):
        if salle not in self.adjacence:
            self.adjacence[salle] = set()
            self.capacites[salle] = float("inf") if salle in (self.vestibule, self.dortoir) else 1

    def ajouter_tunnel(self, a, b):
        self.init_salle(a)
        self.init_salle(b)
        self.adjacence[a].add(b)
        self.adjacence[b].add(a)

    def trouver_chemin(self):
        a_visiter = [[self.vestibule]] 
        visites = {self.vestibule}
        
        while a_visiter:
            chemin = a_visiter.pop(0)
            salle_actuelle = chemin[-1]
            
            if salle_actuelle == self.dortoir:
                return chemin
                
            for voisin in self.adjacence.get(salle_actuelle, []):
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
                    a, b = ligne.split(" - ")
                    colonie.ajouter_tunnel(a.strip(), b.strip())
                elif "{" in ligne:
                    nom, cap = ligne.replace("}", "").split("{")
                    colonie.init_salle(nom.strip())
                    colonie.capacites[nom.strip()] = int(cap.strip())
                else:
                    colonie.init_salle(ligne)

        if not colonie.nb_fourmis:
            raise ValueError("Nombre de fourmis manquant.")
        return colonie

    def simuler(self, chemin):
        fourmis = {i: 0 for i in range(1, self.nb_fourmis + 1)}
        etape = 1
        
        while fourmis:
            mouvements = []
            occupations = {salle: 0 for salle in chemin}
            
            for f_id, idx in list(fourmis.items()):
                salle, suivante = chemin[idx], chemin[idx + 1]
                
                if occupations[suivante] < self.capacites.get(suivante, 1):
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
        G = nx.Graph(self.adjacence)
        couleurs = ["lightgreen" if n == self.vestibule else "salmon" if n == self.dortoir else "lightblue" for n in G.nodes()]
        
        plt.figure(figsize=(10, 7))
        nx.draw(G, with_labels=True, node_color=couleurs, node_size=1500, font_weight="bold", edge_color="gray")
        plt.title(f"Réseau de la Fourmilière ({self.nb_fourmis} fourmis)")
        plt.show()

    def __repr__(self):
        return f"Fourmiliere(F={self.nb_fourmis}, Salles={len(self.adjacence)}, valide={bool(self.trouver_chemin())})"