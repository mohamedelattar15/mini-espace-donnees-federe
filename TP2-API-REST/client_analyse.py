"""TP2 - Client du laboratoire (organisation C).

Interroge les deux API, associe les données par date et compare les
admissions pendant les journées de pollution élevée (PM2.5 > 30) et
non élevée.

Attention : dans cette version, le laboratoire reçoit les données
brutes des deux organisations.
"""

import requests

URL_AIR = "http://127.0.0.1:8001"
URL_HOPITAL = "http://127.0.0.1:8002"
SEUIL_PM25 = 30


def recuperer_mesures_air():
    r = requests.get(f"{URL_AIR}/mesures", timeout=5)
    r.raise_for_status()
    return r.json()


def recuperer_admissions():
    r = requests.get(f"{URL_HOPITAL}/admissions", timeout=5)
    r.raise_for_status()
    return r.json()


def comparer_admissions(mesures_air, admissions):
    """Compare les admissions selon la catégorie de pollution."""
    air_par_date = {x["date"]: x["pm25"] for x in mesures_air}
    hopital_par_date = {x["date"]: x["nombre"] for x in admissions}

    elevees = []
    non_elevees = []

    print("Date | PM2.5 | Admissions")
    for date in sorted(air_par_date.keys() & hopital_par_date.keys()):
        pm25 = air_par_date[date]
        nombre = hopital_par_date[date]
        print(date, "|", pm25, "|", nombre)
        if pm25 > SEUIL_PM25:
            elevees.append(nombre)
        else:
            non_elevees.append(nombre)

    print("Moyenne admissions, pollution élevée :",
          round(sum(elevees) / len(elevees), 2))
    print("Moyenne admissions, autres jours :",
          round(sum(non_elevees) / len(non_elevees), 2))


if __name__ == "__main__":
    comparer_admissions(recuperer_mesures_air(), recuperer_admissions())
