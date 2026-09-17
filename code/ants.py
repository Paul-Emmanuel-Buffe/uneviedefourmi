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
            self.adjacence[nom_salle] = set() # L'utilisation d'un set évite les doublons de tunnels
            self.capacites[nom_salle] = self.CAPACITE_ILLIMITE if nom_salle in (self.vestibule, self.dortoir) else self.CAPACITE_PAR_DEFAUT

    def ajouter_tunnel(self, salle_a, salle_b):
        self.ajouter_salle(salle_a)
        self.ajouter_salle(salle_b)
        self.adjacence[salle_a].add(salle_b)
        self.adjacence[salle_b].add(salle_a)

    def definir_capacite(self, salle, capacite):
        self.ajouter_salle(salle)
        self.capacites[salle] = capacite

    def est_valide(self):
        if self.vestibule not in self.adjacence or self.dortoir not in self.adjacence:
            return False
            
        a_visiter = [self.vestibule]
        visites = {self.vestibule}
        
        while a_visiter:
            salle = a_visiter.pop(0)
            if salle == self.dortoir:
                return True
            for voisin in self.adjacence.get(salle, set()):
                if voisin not in visites:
                    visites.add(voisin)
                    a_visiter.append(voisin)
        return False

    @classmethod 
    def depuis_fichier(cls, chemin_fichier):
        colonie = cls()
        with open(chemin_fichier, encoding="utf-8") as fichier:
            # Nettoyage direct à la volée en ignorant les lignes vides
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

    def __repr__(self):
        return f"Fourmiliere(F={self.nb_fourmis}, Salles={len(self.adjacence)}, valide={self.est_valide()})"