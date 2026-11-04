"""TP3 - Client du laboratoire (organisation C).

Récupère les catégories de pollution auprès de A, puis demande à B de
calculer les statistiques localement. Le laboratoire n'accède jamais
aux bases des organisations.
"""

import os

import requests

URL_AIR = "http://127.0.0.1:8001"
URL_HOPITAL = "http://127.0.0.1:8002"

# Clés de démonstration : ne jamais les utiliser avec des données réelles.
CLE_AIR = os.getenv("CLE_ENVIRONNEMENT", "demo-air-123")
CLE_HOPITAL = os.getenv("CLE_HOPITAL", "demo-hopital-456")


def recuperer_categories():
    r = requests.get(
        f"{URL_AIR}/categories",
        headers={"X-API-Key": CLE_AIR},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()


def demander_analyse(classifications):
    r = requests.post(
        f"{URL_HOPITAL}/analyse-locale",
        headers={"X-API-Key": CLE_HOPITAL},
        json={"classifications": classifications},
        timeout=5,
    )
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    resultats = demander_analyse(recuperer_categories())
    elevee = resultats["elevee"]
    non_elevee = resultats["non_elevee"]

    print("--- Analyse régionale ---")
    print("Pollution élevée :", elevee)
    print("Pollution non élevée :", non_elevee)

    if (elevee["moyenne_admissions"] is not None
            and non_elevee["moyenne_admissions"] is not None):
        difference = (
            elevee["moyenne_admissions"]
            - non_elevee["moyenne_admissions"]
        )
        print("Différence entre les moyennes :", round(difference, 2))
