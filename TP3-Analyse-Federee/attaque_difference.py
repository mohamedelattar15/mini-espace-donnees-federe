"""TP3 - Mise à l'épreuve : l'attaque par différence.

Le laboratoire choisit lui-même le groupe de dates (un seul jour) et
retrouve ainsi une valeur quasi individuelle, malgré l'agrégation.
"""

import os

import requests

URL_HOPITAL = "http://127.0.0.1:8002"
# Clé de démonstration : ne jamais l'utiliser avec des données réelles.
CLE_HOPITAL = os.getenv("CLE_HOPITAL", "demo-hopital-456")

# Le laboratoire choisit LUI-MÊME le groupe : un seul jour.
DEMANDE = {
    "classifications": [
        {"date": "2026-10-01", "categorie": "non_elevee"}
    ]
}

if __name__ == "__main__":
    r = requests.post(
        f"{URL_HOPITAL}/analyse-locale",
        headers={"X-API-Key": CLE_HOPITAL},
        json=DEMANDE,
        timeout=5,
    )
    print(r.json())
