from ants import Fourmiliere


NOM_FICHIER = "../data/salle_d_at-ant.txt"


def main():

    # --- Construction de la fourmilière ---
    try:
        colonie = Fourmiliere.depuis_fichier(NOM_FICHIER)
    except (FileNotFoundError, ValueError) as erreur:
        print(f"Erreur de lecture du fichier : {erreur}")
        return

    print(colonie)

    # --- Validation : Sv et Sd doivent exister et être connectés ---
    if not colonie.est_valide():
        print("Aucun chemin entre le vestibule et le dortoir : fourmilière invalide.")
        return

    print(f"Nombre de fourmis à déplacer : {colonie.nb_fourmis}")
    print(f"Nombre de salles              : {colonie.nb_salles()}")



if __name__ == "__main__":
    main()