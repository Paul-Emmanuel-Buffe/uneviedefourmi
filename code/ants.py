# ants

class Fourmiliere:

    """
    Représentation du réseau de salles et tunnels, sans dépendance :
        - l'adjacence est un simple dictionnaire {salle: [liste de salles voisines]}
        - Vestibule et dortoir ont un capacité illimitée
        - une salle a une capacité de 1, sauf si le fichier apporte une précision
        - Tunnels: n'ont aucune capacité (non-orientés)
    """

    CAPICITE_PAR_DEFAUT = 1
    CAPACITE_ILLIMITE = float("inf")

    def __init__(self, vestibule="Sv", dortoir="Sd"):
        self.adjacence = {} # Le graph: salle -> salles voisines. Un graph = des sommets et des relations / capacité = propriété porté par un sommet (pas le graph lui-même)
        self.capacites = {}
        self.vestibule = vestibule
        self.dortoir = dortoir
        self.nb_fourmis = None

# Construction du graph: ajouter_salle et ajouter_tunnel
    def ajouter_salle(self, nom_salle):
        if nom_salle not in self.adjacence:
            self.adjacence[nom_salle] = []

            # permet d'écraser la capacité classique d'une salle au cas où le fichier en définie une:
            self.capacites[nom_salle] = self._capacite_par_defaut(nom_salle)

    def ajouter_tunnel(self, salle_a, salle_b):
        self.ajouter_salle(salle_a) 
        self.ajouter_salle(salle_b)

        # Un tunnel peut etre parcouru dans les 2 sens (graph non orienté)
        if salle_b not in self.adjacence[salle_a]:
            # sens declaré dans le fichier
            self.adjacence[salle_a]  .append(salle_b)

        if salle_a not in self.adjacence[salle_b]:
            # sens inverse
            self.adjacence[salle_b].append(salle_a)

# Gestion des capacités des salles: definir_capacite et _capacite_par_defaut

    def definir_capacite(self, salle, capacite):
        self.ajouter_salle(salle)
        self.capacites[salle] = capacite

    def _capacite_par_defaut(self, salle): # syntaxe '_' = outil interne
        if salle in (self.vestibule, self.dortoir):
            return self.CAPACITE_ILLIMITE
        return self.CAPICITE_PAR_DEFAUT

    # Voisins, nb_salles, capacite : Consultation seule

    def voisins(self, salle): 
        return self.adjacence.get(salle, []) # get() évite KeyError si une salle n'a pas de voisin.

    def nb_salles (self):
        return len(self.adjacence)

    def capacite (self, salle):
        return self.capacites.get(salle, self.CAPICITE_PAR_DEFAUT) # sécurité au cas où la salle n'a pas encore de capacité renseignée

    # Validation et connexité: est_valide & _chemin_existe

    def est_valide(self):
        # verifie que Sv et Sd existent, et qu'un chemin les reli
        if self.vestibule not in self.adjacence or self.dortoir not in self.adjacence:
            return False
        return self._chemin_existe(self.vestibule, self.dortoir)

    # L'éclaireur, trouve le dortoir et vérifie que l'on ne tourne pas en rond
    def _chemin_existe(self, depart, arrivee):
        a_visiter = [depart] # File d'attente: on y est pas encore entré
        visites = {depart} # Salle où on ai déjà allé (evite de tourner en rond)
        # début de la boucle
        while a_visiter:
            salle = a_visiter.pop(0) # On rentre dans la salle

            # condition d'arrêt
            if salle == arrivee: # vérification que l'on est pas dans le dortoir
                return True

            for voisin in self.voisins(salle):
                if voisin not in visites:
                    visites.add(voisin) # ajout de la salles aux visitées, pas besoin d'y retourner
                    a_visiter.append(voisin)# a explorer plus tard
        return False # Impasse: on a tout visiter mais on a jamais trouvé le Sd

    @classmethod 
    # @classmethod : indique une méthode "usine".
    # Elle reçoit "cls" (la classe, le plan d'architecte) plutôt que "self" (une fourmilière déjà bâtie)
    # afin de créer, charger et renvoyer une TOUTE NOUVELLE instance (un objet concret en mémoire).

    def depuis_fichier(cls, chemin_fichier):
        """
            Construit une Fourmiliere à partir d'un fichier au format du projet :
                f=<nombre de fourmis>      (F= accepté aussi, casse indifférente)
                <salle>                    (capacité par défaut)
                <salle> { <capacite> }     (capacité explicite)
                <salle_a> - <salle_b>      (tunnel)
        """
        colonie = cls() # cls représente la colonie elle-même

        with open(chemin_fichier, encoding="utf-8") as fichier:
            for ligne_brute in fichier:
                ligne = ligne_brute.strip() # retrait des espaces et saut à la ligne
                if not ligne: # on ignore les lignes vides
                    continue

                # Le parseur
                if ligne[0] in ("f", "F") and "=" in ligne: # Nb fourmis
                    colonie.nb_fourmis = int(ligne.split("=")[1].strip()) # on découpe la syntaxe pour lire la valeur de f + conversion de str en int

                # Les tunnels
                elif " - " in ligne:
                    salle_a, salle_b = (s.strip() for s in ligne.split(" - "))
                    colonie.ajouter_tunnel(salle_a, salle_b)

                # Les salles avec capacités définies
                elif "{" in ligne:
                    nom, reste = ligne.split("{", 1) # découpe la ligne de texte
                    capacite = int(reste.replace("}", "").strip())# suppression { pour isoler la valeur + conversion de la valeur en int
                    colonie.definir_capacite(nom.strip(), capacite)
                else:
                    colonie.ajouter_salle(ligne) # enregistrement pas défaut des salles classiques (aucune condition précédente remplie)

        if colonie.nb_fourmis is None:
            # cas infos manquantes pour Nb f non renseigné
            raise ValueError (f"Nombre de fourmis manquant dans {chemin_fichier}")
        return colonie

    def __repr__(self):
        # vérification / debug
        return (f"Fourmilière(F={self.nb_fourmis},"
                f"Salles={self.nb_salles()}, valide={self.est_valide()})")