"""TP1 - Consultation des deux bases fédérées.

Les deux jeux de données restent dans deux fichiers distincts :
aucune jointure SQL n'est possible entre les organisations.
"""

import sqlite3

REQUETES = [
    ("environnement.db", "SELECT * FROM qualite_air ORDER BY date"),
    ("hopital.db", "SELECT * FROM admissions ORDER BY date"),
]


def afficher_base(fichier, requete):
    """Affiche le contenu d'une base pour une requête donnée."""
    print("\nBase :", fichier)
    db = sqlite3.connect(fichier)
    for ligne in db.execute(requete):
        print(ligne)
    db.close()


if __name__ == "__main__":
    for fichier, requete in REQUETES:
        afficher_base(fichier, requete)
