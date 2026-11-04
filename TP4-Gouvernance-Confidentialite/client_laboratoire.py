"""TP4 - Étape 3 : nœud C (Laboratoire).

Orchestrateur : découvre le catalogue, négocie un contrat, récupère les
classifications signées et les transmet à l'hôpital. Il n'accède jamais
directement aux fichiers SQLite des organisations.

Usage :
    python client_laboratoire.py
    python client_laboratoire.py --bruit
"""

import sys

import requests

URL_AIR = "http://127.0.0.1:8001"
URL_HOPITAL = "http://127.0.0.1:8002"

# Valeurs de démonstration : à ne JAMAIS utiliser en production.
CLE_A = "secret-air-key-demo"
CLE_B = "secret-hospital-key-demo"
CONSUMER_ID = "laboratoire-iasd"
DATASET_ID = "dataset-air-tanger"

TIMEOUT = 10


def negocier(session, purpose, cle=CLE_A, dataset_id=DATASET_ID):
    return session.post(
        f"{URL_AIR}/contracts/negotiate",
        json={
            "dataset_id": dataset_id,
            "consumer_id": CONSUMER_ID,
            "purpose": purpose,
        },
        headers={"X-API-Key": cle},
        timeout=TIMEOUT,
    )


def executer_scenario(apply_noise=False, epsilon=1.0):
    session = requests.Session()

    print("1. Découverte du catalogue")
    r = session.get(f"{URL_AIR}/catalog", timeout=TIMEOUT)
    r.raise_for_status()
    print("  ", r.json()[0]["title"])

    print("\n2. Tests négatifs")
    r = negocier(session, "commercial")
    print(f"   Finalité commerciale : attendu 403, reçu {r.status_code}")
    r = negocier(session, "research", dataset_id="dataset-inconnu")
    print(
        "   Jeu de données inexistant : attendu 404, "
        f"reçu {r.status_code}"
    )
    r = negocier(session, "research", cle="mauvaise-cle")
    print(f"   Clé API incorrecte : attendu 401, reçu {r.status_code}")

    print("\n3. Demande autorisée pour la recherche")
    r = negocier(session, "research")
    r.raise_for_status()
    contract_id = r.json()["contract_id"]
    print("   Accord obtenu :", contract_id)

    print("\n4. Récupération des classifications")
    r = session.get(
        f"{URL_AIR}/classifications",
        params={"contract_id": contract_id, "consumer_id": CONSUMER_ID},
        headers={"X-API-Key": CLE_A},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    paquet = r.json()
    print("   Nombre de jours classifiés :", len(paquet["classifications"]))

    print(
        "\n5. Calcul réalisé par l'hôpital",
        "(avec bruit)" if apply_noise else "(sans bruit)",
    )
    r = session.post(
        f"{URL_HOPITAL}/compute",
        json={**paquet, "apply_dp": apply_noise, "epsilon": epsilon},
        headers={"X-API-Key": CLE_B},
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    res = r.json()

    for nom, cle in [
        ("Pollution au-dessus du seuil", "au_dessus_seuil"),
        ("Pollution sous le seuil", "sous_seuil"),
    ]:
        g = res[cle]
        print(
            f"   {nom} : n={g['n']}, moyenne={g['moyenne']}, "
            f"statut={g['statut']}"
        )

    a = res["au_dessus_seuil"]["moyenne"]
    b = res["sous_seuil"]["moyenne"]
    if a is not None and b is not None:
        print(f"   Différence : {a - b:.2f} admissions/jour")

    print(
        "\n6. Test négatif : classifications falsifiées envoyées à l'hôpital"
    )
    faux = dict(paquet)
    # Sous-ensemble choisi par le laboratoire : la signature ne correspond plus.
    faux["classifications"] = paquet["classifications"][:4]
    r = session.post(
        f"{URL_HOPITAL}/compute",
        json=faux,
        headers={"X-API-Key": CLE_B},
        timeout=TIMEOUT,
    )
    print(f"   Attendu 403 (signature invalide), reçu {r.status_code}")


if __name__ == "__main__":
    executer_scenario(apply_noise="--bruit" in sys.argv)
