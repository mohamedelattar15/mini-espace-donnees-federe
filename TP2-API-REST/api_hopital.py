"""TP2 - API de l'organisation B (Hôpital).

Expose les admissions respiratoires stockées dans hopital.db.
Port : 8002
"""

import sqlite3

from fastapi import FastAPI

app = FastAPI(title="API Hôpital")


def ouvrir_base():
    """Ouvre la base locale de l'organisation B."""
    db = sqlite3.connect("hopital.db")
    db.row_factory = sqlite3.Row
    return db


@app.get("/")
def accueil():
    return {"organisation": "Hôpital régional"}


@app.get("/admissions")
def obtenir_admissions():
    db = ouvrir_base()
    lignes = db.execute("""
        SELECT date, ville, nombre
        FROM admissions ORDER BY date
    """).fetchall()
    db.close()
    return [dict(ligne) for ligne in lignes]


@app.get("/statistiques")
def statistiques():
    db = ouvrir_base()
    resultat = db.execute("""
        SELECT COUNT(*), AVG(nombre) FROM admissions
    """).fetchone()
    db.close()
    return {
        "nombre_jours": resultat[0],
        "moyenne_admissions": round(resultat[1], 2),
    }
