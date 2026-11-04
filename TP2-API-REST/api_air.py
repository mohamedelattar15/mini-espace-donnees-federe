"""TP2 - API de l'organisation A (Environnement).

Expose les mesures de PM2.5 stockées dans environnement.db.
Port : 8001
"""

import sqlite3

from fastapi import FastAPI

app = FastAPI(title="API Environnement")


def ouvrir_base():
    """Ouvre la base locale de l'organisation A."""
    db = sqlite3.connect("environnement.db")
    db.row_factory = sqlite3.Row
    return db


@app.get("/")
def accueil():
    return {"organisation": "Direction de l'environnement"}


@app.get("/mesures")
def obtenir_mesures():
    db = ouvrir_base()
    lignes = db.execute("""
        SELECT date, ville, pm25
        FROM qualite_air ORDER BY date
    """).fetchall()
    db.close()
    return [dict(ligne) for ligne in lignes]


@app.get("/statistiques")
def statistiques():
    db = ouvrir_base()
    resultat = db.execute("""
        SELECT COUNT(*), AVG(pm25) FROM qualite_air
    """).fetchone()
    db.close()
    return {
        "nombre_jours": resultat[0],
        "moyenne_pm25": round(resultat[1], 2),
    }
