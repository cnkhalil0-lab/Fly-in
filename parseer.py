

class Zone:
    def __init__(self, nom, x, y, couleur=None, parking=1, type="normal"):
        self.nom = nom
        self.x = x
        self.y = y
        self.couleur = couleur
        self.parking = parking
        self.type = type
        self.vois = {}

    def add_voisins(self, target, max_link_capacity=1):
        self.vois[target] = max_link_capacity


class Map:
    def __init__(self):
        self.depart = None
        self.arrivee = None
        self.nbr_drone = 0
        self.zones = {}


class parser:
    def __init__(self, file):
        try:
            with open(file, "r") as fichier:
                self.ma_carte = Map()
                self.compt_ligne = 1
                self.compt_end = 0
                self.compt_start = 0
                for ligne in fichier:
                    couleur = None
                    paarking = 1
                    max_link_capacity = 1
                    type_zone = "normal"

                    contenue = ligne.split()
                    args1 = contenue

                    if not args1:
                        continue

                    if '[' in ligne:
                        contenue = ligne.split('[')
                        args1 = contenue[0].split()
                        args2 = contenue[1].replace(']', '')
                        args2 = args2.split()

                        if contenue:
                            for options in args2:
                                argument = options.split('=')
                                cle = argument[0]
                                valeur = argument[1]
                                if cle == "color":
                                    couleur = valeur
                                elif cle == "max_drones":
                                    paarking = int(valeur)
                                    if paarking < 1:
                                        return (f"Error: le max des drones dans la station est invalide - ligne {self.compt_ligne}")
                                elif cle == "max_link_capacity":
                                    max_link_capacity = valeur
                                elif cle == "zone":
                                    type_zone = valeur
                                    if type_zone not in ["normal", "restricted", "bloqued"]:
                                        return (f"Error: type de zone non reconnue - ligne {self.compt_ligne}")

                    if args1[0] == ("start_hub:"):
                        self.ma_carte.depart = Zone(args1[1], int(args1[2]), int(args1[3]), couleur, paarking, type_zone)
                        self.ma_carte.zones[self.ma_carte.depart.nom] = self.ma_carte.depart
                        self.compt_start += 1
                        if self.compt_start > 1:
                            return (f"Error: la map contient plusieurs station de depart - ligne {self.compt_ligne}")

                    elif args1[0] == ("end_hub:"):
                        self.ma_carte.arrivee = Zone(args1[1], int(args1[2]), int(args1[3]), couleur, int(paarking), type_zone)
                        self.ma_carte.zones[self.ma_carte.arrivee.nom] = self.ma_carte.arrivee
                        self.compt_end += 1
                        if self.compt_end > 1:
                            return (f"Error: la map contient plusieurs station d arrivee - ligne {self.compt_ligne}")

                    elif args1[0] == ("hub:"):
                        self.ma_carte.zones[args1[1]] = Zone(args1[1], int(args1[2]), int(args1[3]), couleur, int(paarking), type_zone)

                    elif args1[0] == ("connection:"):
                        option_args1 = args1[1].split('-')
                        try:
                            self.ma_carte.zones[option_args1[0]].add_voisins(self.ma_carte.zones[option_args1[1]], int(max_link_capacity))
                            self.ma_carte.zones[option_args1[1]].add_voisins(self.ma_carte.zones[option_args1[0]], int(max_link_capacity))
                        except KeyError:
                            return (f"station introuvable - ligne : {self.compt_ligne}")
                    elif args1[0] == "nb_drones:":
                        self.ma_carte.nbr_drone = int(args1[1])
                        if self.ma_carte.nbr_drone < 1:
                            return (f"nombre de drone invalide{self.compt_ligne}")
                    self.compt_ligne += 1
                if self.compt_start == 0:
                    return ("Error: station de depart introuvable")
                if self.compt_end == 0:
                    return ("Error: station d arrivee introuvable")

        except FileNotFoundError:
            print(f"le fichier {file} n existe pas")

    # def blindage_parser(self):
    #     if self.ma_carte.nbr_drone < 1:
    #         return "nombre de drone invalide"
    #     if self.compt_end != 1 or self.compt_start != 1:
    #         if self.compt_end == 0:
    #             return ("Error: station d arrivee introuvable")
    #         elif self.compt_end > 1:
    #             return ("Error: la map contientplusieurs station d arrivee")
    #         if self.compt_start == 0:
    #             return ("Error: station d arrivee introuvable")
    #         elif self.compt_start > 1:
    #             return ("Error: la map contientplusieurs station d arrivee")


class Drone:
    def __init__(self, nom, chemin, index_station, etat_vol):
        self.nom = nom
        self.chemin = chemin
        self.index_station = index_station
        self.etat_vol = etat_vol


class simulateur():
    def __init__(self, txt):
        self.carte = parser(txt)
        self.carte_algo = parser(txt)

        self.chemins = algo_bahandri(self.carte_algo)
        self.listes_drones = []
        self.nbr_drones = self.carte.ma_carte.nbr_drone
        for i in range(1, self.nbr_drones+1):
            self.listes_drones.append(Drone(f"D{i}", self.chemin, 0, 0))

    def moteur(self):
        COULEURS = {
                    "red": "\033[91m",
                    "blue": "\033[94m",
                    "green": "\033[92m",
                    "reset": "\033[0m",
                    "yellow": "\033[93m",
                    "cyan": "\033[96m"
                }
        while min(self.listes_drones, key=lambda x: x.index_station).index_station < (len(self.chemin)-1):
            self.listes_drones.sort(key=lambda x: x.index_station, reverse=True)
            boite_operations = []
            journal_opperations = {}
            for drone_actuelle in self.listes_drones:
                if drone_actuelle.index_station == (len(drone_actuelle.chemin) - 1):
                    continue
                elif drone_actuelle.etat_vol == 1:
                    drone_actuelle.etat_vol = 0
                else:
                    ma_route = f"{drone_actuelle.chemin[drone_actuelle.index_station]}-{drone_actuelle.chemin[drone_actuelle.index_station + 1]}"
                    journal_opperations[ma_route] = journal_opperations.get(ma_route, 0)
                    max_support_route = self.carte.ma_carte.zones[self.chemin[drone_actuelle.index_station]].vois[self.carte.ma_carte.zones[self.chemin[drone_actuelle.index_station + 1]]]

                    couleurr = self.carte.ma_carte.zones[self.chemin[drone_actuelle.index_station + 1]].couleur
                    if couleurr in COULEURS:
                        ma_couleur = COULEURS[couleurr]
                    else:
                        ma_couleur = ""
                    if drone_actuelle.chemin[drone_actuelle.index_station + 1] != self.carte.ma_carte.arrivee.nom:
                        i = 0
                        for element in self.listes_drones:
                            if element.chemin[element.index_station] == drone_actuelle.chemin[(drone_actuelle.index_station)+1]:
                                i += 1
                        if i < self.carte.ma_carte.zones[self.chemin[drone_actuelle.index_station + 1]].parking:
                            if journal_opperations[ma_route] < max_support_route:
                                drone_actuelle.index_station += 1
                                journal_opperations[ma_route] += 1
                                boite_operations.append(f"{ma_couleur}{drone_actuelle.nom}-{self.chemin[drone_actuelle.index_station]}{COULEURS['reset']}")
                                if self.carte.ma_carte.zones[self.chemin[drone_actuelle.index_station]].type == "restricted":
                                    drone_actuelle.etat_vol = 1

                    elif drone_actuelle.index_station < (len(self.chemin)-1):
                        if journal_opperations[ma_route] < max_support_route:
                            drone_actuelle.index_station += 1
                            journal_opperations[ma_route] += 1
                            boite_operations.append(f"{ma_couleur}{drone_actuelle.nom}-{self.chemin[drone_actuelle.index_station]}{COULEURS['reset']}")

            if len(boite_operations) > 0:
                print(boite_operations)


def algo_bahandri(map):
    chemin = algo_dijkstra(map)
    sac_des_paires = []
    while chemin != "aucun trajet disponible":
        for i in range(len(chemin)-1):
            station_actuelle = chemin[i]
            station_suivante = chemin[i+1]
            map.ma_carte.zones[station_actuelle].vois.pop(map.ma_carte.zones[station_suivante], None)
            map.ma_carte.zones[station_suivante].vois[map.ma_carte.zones[station_actuelle]] = -1
        for i in range(len(chemin)-1):
            sac_des_paires.append((chemin[i], chemin[i+1]))
        chemin = algo_dijkstra(map)
    nv_sac_des_paires = []
    for i in range(len(sac_des_paires)):
        cable_inverse = (sac_des_paires[i][1], sac_des_paires[i][0])
        if cable_inverse in sac_des_paires:
            continue
        nv_sac_des_paires.append(sac_des_paires[i])
    sac_des_chemins = []
    while list(filter((lambda x: x[0] == map.ma_carte.depart.nom), nv_sac_des_paires)):
        chemin_act = [map.ma_carte.depart.nom]
        station_act = map.ma_carte.depart.nom
        while station_act != map.ma_carte.arrivee.nom:
            for a in nv_sac_des_paires:
                if station_act == a[0]:
                    station_act = a[1]
                    chemin_act.append(a[1])
                    nv_sac_des_paires.remove(a)
                    break
            else:
                break
        if map.ma_carte.arrivee.nom in chemin_act:
            sac_des_chemins.append(chemin_act)
        else:
            continue
    return sac_des_chemins


def algo_dijkstra(maap):
    scores = {}
    file_datt = []
    came_from = {}

    for i in maap.ma_carte.zones:
        scores[i] = float('inf')
    scores[maap.ma_carte.depart.nom] = 0
    came_from[maap.ma_carte.depart.nom] = None
    file_datt = [(0, maap.ma_carte.depart.nom)]

    while file_datt:
        if file_datt[0][1] == maap.ma_carte.arrivee.nom:
            break

        station_actuelle = file_datt[0][1]
        chrono_actuelle = file_datt[0][0]
        file_datt.pop(0)

        for a in maap.ma_carte.zones[station_actuelle].vois:
            valeur_max_link = maap.ma_carte.zones[station_actuelle].vois[a]
            if valeur_max_link == -1:
                count = -1
            else:
                count = 1
                if a.type == "restricted":
                    count = 2
                elif a.type == "blocked":
                    continue
            nouveau_chrono = chrono_actuelle + count

            if scores[a.nom] > nouveau_chrono:
                scores[a.nom] = nouveau_chrono
                file_datt.append((nouveau_chrono, a.nom))
                file_datt.sort()
                came_from[a.nom] = station_actuelle
            else:
                continue

    if maap.ma_carte.arrivee.nom not in came_from:
        return "aucun trajet disponible"

    station_actuelle = maap.ma_carte.arrivee.nom
    chemin_finale = [station_actuelle]

    while came_from[station_actuelle] is not None:
        station_actuelle = came_from[station_actuelle]
        chemin_finale.append(station_actuelle)

    chemin_finale.reverse()
    return chemin_finale
