from ants import AntColony


FILE_NAME = "../data/fourmiliere_3D.txt"

def main():
    try:
        colony = AntColony.from_file(FILE_NAME)
    except (FileNotFoundError, ValueError) as error:
        print(f"Erreur de lecture du fichier : {error}")
        return

    print(colony)
    print("Affichage du graphe en cours ...")
    colony.display_graph()

    print("\n" + "="*25)
    print("DEPLACEMENT DES FOURMIS")
    print("="*25 + "\n")

    distances = colony.calculate_distances()
    
    if not distances:
        print("fourmilière invalide.")
        return
        
    # Simulation
    colony.simulate(distances)


if __name__ == "__main__":
    main()