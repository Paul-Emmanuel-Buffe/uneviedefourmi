from ants import Fourmiliere

NOM_FICHIER = "../data/salle_d_at-ant.txt"

def main():
    try:
        colonie = Fourmiliere.depuis_fichier(NOM_FICHIER)
    except (FileNotFoundError, ValueError) as erreur:
        print(f"Erreur de lecture du fichier : {erreur}")
        return

    print(colonie)
    
    # --- Affichage visuel du graphe ---
    print("Affichage du graphe en cours (fermez la fenêtre pour lancer la simulation)...")
    colonie.afficher_graphe()

    chemin_optimal = colonie.trouver_chemin()

    if not chemin_optimal:
        print("Aucun chemin entre le vestibule et le dortoir : fourmilière invalide.")
        return

    print(f"Chemin emprunté               : {' -> '.join(chemin_optimal)}")
    print("\n" + "="*30)
    print("     DÉBUT DE LA SIMULATION")
    print("="*30 + "\n")

    colonie.simuler(chemin_optimal)

if __name__ == "__main__":
    main()