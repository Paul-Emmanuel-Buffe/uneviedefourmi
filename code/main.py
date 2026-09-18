import sys
from ants import AntColony

# Fichier par défaut si aucun n'est fourni dans le terminal
FILE_NAME = sys.argv[1] if len(sys.argv) > 1 else "../data/fourmiliere_quatre.txt"

def main():
    try:
        colony = AntColony.from_file(FILE_NAME)
    except (FileNotFoundError, ValueError) as error:
        print(f"Erreur de lecture du fichier : {error}")
        return

    print(colony)
    print(f"Nombre de salles              : {len(colony.adjacency)}")

    print("Affichage du graphe en cours ...")
    if hasattr(colony, 'display_graph'):
        colony.display_graph()

    print("\n" + "="*30)
    print("     DÉBUT DE LA SIMULATION")
    print("="*30 + "\n")

    if hasattr(colony, 'calculate_distances'):
        distances = colony.calculate_distances()
        if not distances:
            print("fourmilière invalide.")
            return
        colony.simulate(distances)
        
    elif hasattr(colony, 'find_path'):
        best_path = colony.find_path()
        if not best_path:
            print("Aucun chemin entre vestibule et  dortoir => fourmilière invalide.")
            return
        print(f"Chemin pris              : {' -> '.join(best_path)}\n")
        colony.simulate(best_path)
        
    else:
        print("Erreur : Aucune méthode de parcours compatible trouvée dans la classe.")

if __name__ == "__main__":
    main()