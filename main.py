from ants import Anthill


anthill = Anthill()

anthill.parse_file(
    "maps/fourmiliere_un.txt"
)

anthill.simulate()