"""TP3 - API protégée de l'organisation A (Environnement).

Ne transmet plus les concentrations exactes : uniquement la catégorie
de pollution de chaque journée (elevee si PM2.5 > 30, non_elevee sinon).
Accès protégé par une clé API de démonstration.
Port : 8001
"""

import os
import sqlite3

from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="API Environnement - TP3")

# Clé de démonstration : ne jamais l'utiliser avec des données réelles.
CLE_API = os.getenv("CLE_ENVIRONNEMENT", "demo-air-123")
SEUIL_PM25 = 30


def verifier_cle(x_api_key):
    if x_api_key != CLE_API:
        raise HTTPException(status_code=401, detail="Clé API invalide")


@app.get("/")
def accueil():
    return {"organisation": "Direction de l'environnement"}


@app.get("/categories")
def categories(x_api_key: str = Header(default="")):
    verifier_cle(x_api_key)
    db = sqlite3.connect("environnement.db")
    lignes = db.execute("""
        SELECT date,
          CASE WHEN pm25 > ? THEN 'elevee'
               ELSE 'non_elevee' END
        FROM qualite_air ORDER BY date
    """, (SEUIL_PM25,)).fetchall()
    db.close()
    return [
        {"date": date, "categorie": categorie}
        for date, categorie in lignes
    ]
