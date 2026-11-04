"""TP1 - Stockage fédéré : création de deux bases SQLite indépendantes.

Organisation A (environnement) -> environnement.db
Organisation B (hôpital)       -> hopital.db
"""

import sqlite3

DONNEES_AIR = [
    ("2026-10-01", "Tanger", 12),
    ("2026-10-02", "Tanger", 35),
    ("2026-10-03", "Tanger", 42),
    ("2026-10-04", "Tanger", 15),
    ("2026-10-05", "Tanger", 38),
]

DONNEES_HOPITAL = [
    ("2026-10-01", "Tanger", 8),
    ("2026-10-02", "Tanger", 14),
    ("2026-10-03", "Tanger", 18),
    ("2026-10-04", "Tanger", 9),
    ("2026-10-05", "Tanger", 16),
]


def creer_base_air():
    """Crée la base de l'organisation A et insère les mesures de PM2.5."""
    db_air = sqlite3.connect("environnement.db")
    db_air.execute("""
        CREATE TABLE IF NOT EXISTS qualite_air (
            date TEXT PRIMARY KEY,
            ville TEXT,
            pm25 REAL
        )
    """)
    db_air.execute("DELETE FROM qualite_air")
    db_air.executemany(
        "INSERT INTO qualite_air VALUES (?, ?, ?)", DONNEES_AIR
    )
    db_air.commit()
    db_air.close()


def creer_base_hopital():
    """Crée la base de l'organisation B et insère les admissions."""
    db_hopital = sqlite3.connect("hopital.db")
    db_hopital.execute("""
        CREATE TABLE IF NOT EXISTS admissions (
            date TEXT PRIMARY KEY,
            ville TEXT,
            nombre INTEGER
        )
    """)
    db_hopital.execute("DELETE FROM admissions")
    db_hopital.executemany(
        "INSERT INTO admissions VALUES (?, ?, ?)", DONNEES_HOPITAL
    )
    db_hopital.commit()
    db_hopital.close()


if __name__ == "__main__":
    creer_base_air()
    creer_base_hopital()
    print("Deux bases locales ont été créées.")
