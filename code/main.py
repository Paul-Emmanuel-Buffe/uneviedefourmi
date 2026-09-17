import sys


from ants import Fourmiliere
# from one_by_one import Fourmiliere

# Permet de glisser un autre fichier texte en argument dans le terminal si besoin
NOM_FICHIER = sys.argv[1] if len(sys.argv) > 1 else "../data/La_hormiguera_de_la_muerte.txt"

def main():
    try:
        colonie = Fourmiliere.depuis_fichier(NOM_FICHIER)
    except (FileNotFoundError, ValueError) as erreur:
        print(f"Erreur de lecture du fichier : {erreur}")
        return

    print(colonie)
    print(f"Nombre de salles              : {len(colonie.adjacence)}")

    print("Affichage du graphe en cours (fermez la fenêtre pour lancer la simulation)...")
    if hasattr(colonie, 'afficher_graphe'):
        colonie.afficher_graphe()

    print("\n" + "="*30)
    print("     DÉBUT DE LA SIMULATION")
    print("="*30 + "\n")

    # Détection dynamique de l'algorithme disponible dans le fichier importé
    if hasattr(colonie, 'calculer_distances'):
        distances = colonie.calculer_distances()
        if not distances:
            print("Aucun chemin entre le vestibule et le dortoir : fourmilière invalide.")
            return
        colonie.simuler(distances)
        
    elif hasattr(colonie, 'trouver_chemin'):
        chemin_optimal = colonie.trouver_chemin()
        if not chemin_optimal:
            print("Aucun chemin entre le vestibule et le dortoir : fourmilière invalide.")
            return
        print(f"Chemin emprunté               : {' -> '.join(chemin_optimal)}\n")
        colonie.simuler(chemin_optimal)
        
    else:
        print("Erreur : Aucune méthode de parcours compatible trouvée dans la classe importée.")

if __name__ == "__main__":
    main()