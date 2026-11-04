# Mini-espace de données fédéré — Santé et qualité de l'air

Prototype pédagogique d'**espace de données fédéré** permettant à trois organisations
d'étudier l'association entre la pollution atmosphérique (PM2.5) et les admissions
hospitalières pour affections respiratoires, **sans centraliser les données**.

Projet réalisé dans le cadre du Master IASD — *Data Spaces & Data Integration &
Semantic Interoperability*.

---

## 1. Contexte et problématique

Un espace de données régional est en cours de constitution. Trois acteurs y participent :

| Organisation | Rôle | Données détenues |
|---|---|---|
| **A — Direction régionale de l'environnement** | Producteur | Mesures quotidiennes de PM2.5 |
| **B — Hôpital régional** | Producteur + calculateur | Admissions respiratoires quotidiennes |
| **C — Laboratoire universitaire** | Consommateur | Aucune donnée, uniquement les résultats autorisés |

**Question centrale :**

> Comment analyser ensemble des données détenues par des organisations différentes,
> sans les centraliser, en contrôlant leur usage et en limitant ce qui est révélé ?

Chaque TP apporte une réponse partielle et prépare le suivant :

```
TP1  Stockage fédéré      →  les données restent chez leurs propriétaires
TP2  API REST             →  les organisations communiquent (mais tout est exposé)
TP3  Analyse fédérée      →  le calcul se déplace vers la donnée (mais l'accès est mal contrôlé)
TP4  Gouvernance          →  catalogue, contrat, signature, seuil minimal, bruit
```

---

## 2. Objectifs pédagogiques

- Comprendre le **stockage fédéré** et la conservation des données chez leurs propriétaires.
- Créer et manipuler deux bases **SQLite** locales.
- Exposer des données et des résultats par des **API REST** avec **FastAPI**.
- Interroger des services distincts depuis un **client Python** (`requests`).
- Effectuer des **calculs locaux** et échanger des **statistiques agrégées**.
- Appliquer une **gouvernance** (finalité, contrat, signature) et discuter des **limites
  de la confidentialité**.

---

## 3. Architecture

```
┌──────────────────────────┐        ┌──────────────────────────┐
│  Organisation A          │        │  Organisation B          │
│  Environnement           │        │  Hôpital régional        │
│                          │        │                          │
│  environnement.db        │        │  hopital.db              │
│  (qualite_air)           │        │  (admissions)            │
│         │                │        │         │                │
│  API FastAPI  :8001      │        │  API FastAPI  :8002      │
└─────────┬────────────────┘        └─────────┬────────────────┘
          │                                   │
          │  catégories / classifications     │  agrégats
          │  (jamais les bases)               │
          └───────────────┬───────────────────┘
                          │
                 ┌────────▼─────────┐
                 │  Organisation C  │
                 │  Laboratoire     │
                 │  (client Python) │
                 └──────────────────┘
```

**Principes respectés :**

- Deux bases SQLite **physiquement distinctes** : aucune jointure SQL n'est possible.
- Le laboratoire **n'accède jamais** aux fichiers `.db` ; il ne parle qu'aux API.
- Les ports **8001** (A) et **8002** (B) sont constants sur les quatre TP.
- Les bases du **TP4** (10 jours) sont séparées de celles des **TP1 à TP3** (5 jours).

---

## 4. Technologies utilisées

| Technologie | Usage |
|---|---|
| Python 3.10+ | Langage |
| SQLite (`sqlite3`) | Stockage local |
| FastAPI | API REST |
| Uvicorn | Serveur ASGI |
| Pydantic | Validation des requêtes |
| Requests | Client HTTP du laboratoire |
| `hashlib`, `hmac` | Signature HMAC-SHA256 |
| `json`, `os`, `math`, `random`, `uuid` | Utilitaires standard |

---

## 5. Structure du repository

```
mini-espace-donnees-federe/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── docs/
│   └── Support_TP1_TP4.pdf
│
├── TP1-Stockage-Federe/
│   ├── tp_federation.py
│   └── consulter_bases.py
│
├── TP2-API-REST/
│   ├── api_air.py
│   ├── api_hopital.py
│   └── client_analyse.py
│
├── TP3-Analyse-Federee/
│   ├── api_air_v3.py
│   ├── api_hopital_v3.py
│   ├── laboratoire_v3.py
│   └── attaque_difference.py
│
└── TP4-Gouvernance-Confidentialite/
    ├── setup_data.py
    ├── api_air.py
    ├── api_hopital.py
    └── client_laboratoire.py
```

> Les fichiers `environnement.db` et `hopital.db` sont **générés** à l'exécution et ne sont
> pas versionnés (voir `.gitignore`).

---

## 6. Installation

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloque l'activation des scripts :

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

> Un **environnement virtuel unique** à la racine suffit pour les quatre TP.
> Les commandes suivantes supposent que `.venv` est activé.

---

## 7. TP1 — Stockage fédéré et premières analyses locales

**Objectif :** créer deux bases SQLite indépendantes et constater qu'aucune jointure
SQL n'est possible entre les organisations.

```powershell
cd TP1-Stockage-Federe
python tp_federation.py
python consulter_bases.py
```

**Résultat attendu :**

```
Deux bases locales ont été créées.

Base : environnement.db
('2026-10-01', 'Tanger', 12.0)
...
Base : hopital.db
('2026-10-01', 'Tanger', 8)
...
```

Chaque base contient **cinq enregistrements**.

---

## 8. TP2 — Communication entre organisations avec des API REST

**Objectif :** exposer chaque base par une API et faire communiquer les organisations.
⚠️ Dans cette version, **le laboratoire reçoit les données brutes**.

**Terminal 1 :**

```powershell
cd TP2-API-REST
python -m uvicorn api_air:app --reload --port 8001
```

**Terminal 2 :**

```powershell
cd TP2-API-REST
python -m uvicorn api_hopital:app --reload --port 8002
```

**Terminal 3 :**

```powershell
cd TP2-API-REST
python client_analyse.py
```

> Le TP2 réutilise les bases créées au TP1. Copiez-les si nécessaire :
> `Copy-Item ..\TP1-Stockage-Federe\*.db .`

### Endpoints

| Organisation | Méthode | Route | Description |
|---|---|---|---|
| A | GET | `/` | Identité de l'organisation |
| A | GET | `/mesures` | Mesures PM2.5 brutes |
| A | GET | `/statistiques` | Nombre de jours et moyenne PM2.5 |
| B | GET | `/` | Identité de l'organisation |
| B | GET | `/admissions` | Admissions brutes |
| B | GET | `/statistiques` | Nombre de jours et moyenne admissions |

Documentation interactive : <http://127.0.0.1:8001/docs> et <http://127.0.0.1:8002/docs>.

**Résultat attendu :** moyenne de **16,0** admissions les jours de pollution élevée
contre **8,5** les autres jours.

---

## 9. TP3 — Calculs locaux, contrôle d'accès et analyse fédérée

**Objectif :** ne plus transmettre les concentrations exactes, faire calculer l'hôpital
chez lui, protéger l'accès par une clé API.

**Terminal 1 :**

```powershell
cd TP3-Analyse-Federee
$env:CLE_ENVIRONNEMENT="demo-air-123"
python -m uvicorn api_air_v3:app --reload --port 8001
```

**Terminal 2 :**

```powershell
cd TP3-Analyse-Federee
$env:CLE_HOPITAL="demo-hopital-456"
python -m uvicorn api_hopital_v3:app --reload --port 8002
```

**Terminal 3 :**

```powershell
cd TP3-Analyse-Federee
$env:CLE_ENVIRONNEMENT="demo-air-123"
$env:CLE_HOPITAL="demo-hopital-456"
python laboratoire_v3.py
python attaque_difference.py
```

Sous Linux / macOS, remplacez `$env:VAR="valeur"` par `export VAR="valeur"`.

### Endpoints

| Organisation | Méthode | Route | En-tête | Description |
|---|---|---|---|---|
| A | GET | `/categories` | `X-API-Key` | Dates + catégorie (`elevee` / `non_elevee`) |
| B | POST | `/analyse-locale` | `X-API-Key` | Moyennes calculées localement |

### Tests du contrôle d'accès

| Test | Manipulation | Résultat attendu |
|---|---|---|
| 1 | `/categories` sans clé | 401 |
| 2 | Clé incorrecte | 401 |
| 3 | Bonne clé | 200 |
| 4 | `/analyse-locale` avec mauvaise clé | 401 |
| 5 | Catégorie inconnue | 400 |

**Résultat attendu :** 3 jours à **16,0** vs 2 jours à **8,5**, différence **7,5**.

**Attaque par différence :** en choisissant un seul jour, le laboratoire obtient
`8.0`, soit une valeur quasi individuelle → l'agrégat ne protège pas à lui seul.

---

## 10. TP4 — Gouvernance et confidentialité

**Objectif :** corriger les failles du TP3 par un catalogue, un contrat avec finalité,
une signature HMAC, un seuil minimal de publication et un bruit de Laplace.

**Terminal 1 :**

```powershell
cd TP4-Gouvernance-Confidentialite
python setup_data.py
python -m uvicorn api_air:app --port 8001
```

**Terminal 2 :**

```powershell
cd TP4-Gouvernance-Confidentialite
python -m uvicorn api_hopital:app --port 8002
```

**Terminal 3 :**

```powershell
cd TP4-Gouvernance-Confidentialite
python client_laboratoire.py
python client_laboratoire.py --bruit
```

> ⚠️ Ne pas utiliser `--reload` : les contrats sont stockés **en mémoire** et un
> redémarrage les efface.

### Endpoints

| Organisation | Méthode | Route | En-tête | Description |
|---|---|---|---|---|
| A | GET | `/catalog` | — | Catalogue simplifié inspiré de DCAT |
| A | POST | `/contracts/negotiate` | `X-API-Key` | Négociation selon la finalité |
| A | GET | `/classifications` | `X-API-Key` | Classifications signées (HMAC) |
| B | POST | `/compute` | `X-API-Key` | Agrégats avec seuil minimal et bruit |

Corps de négociation :

```json
{
  "dataset_id": "dataset-air-tanger",
  "consumer_id": "laboratoire-iasd",
  "purpose": "research"
}
```

### Contrôles du nœud B

| Ordre | Contrôle | Code |
|---|---|---|
| 1 | Clé API | 401 |
| 2 | Signature HMAC valide | 403 |
| 3 | Liste non vide, dates uniques, catégories connues, dates présentes | 400 |
| 4 | Budget de confidentialité (`ε` cumulé ≤ 3) | 429 |

### Tests

| Test | Manipulation | Résultat attendu |
|---|---|---|
| Catalogue | `GET /catalog` | 200 |
| Accès autorisé | `purpose = research` | 200 + `contract_id` |
| Finalité non autorisée | `purpose = commercial` | 403 |
| Jeu de données inexistant | `dataset_id` modifié | 404 |
| Clé API incorrecte | `x-api-key` modifiée | 401 |
| Signature falsifiée | sous-ensemble de classifications | 403 |
| Calcul sans bruit | corps copié tel quel | 200, moyennes **16,2** et **7,8** |
| Seuil minimal | groupe de moins de 3 jours | `SUPPRIME_GROUPE_TROP_PETIT` |
| Calcul avec bruit | `"apply_dp": true` | moyennes différentes à chaque appel |
| Budget épuisé | 4ᵉ appel avec bruit et `ε = 1` | 429 |

**Résultat attendu sans bruit :** différence de **8,4** admissions/jour.

---

## 11. Limites et considérations de sécurité

Ce projet est **strictement pédagogique**. Il ne doit **jamais** être exposé sur
Internet ni utilisé avec des données réelles.

- **Clés et secret de démonstration** (`demo-air-123`, `demo-hopital-456`,
  `secret-air-key-demo`, `secret-hospital-key-demo`, `secret-federation-demo`) :
  à remplacer par une gestion sécurisée des secrets en production.
- **Pas de HTTPS** : les échanges circulent en clair sur `127.0.0.1`.
- **Contrats et budgets en mémoire** : perdus au redémarrage du serveur.
- **Seuil de 3 jours ≠ k-anonymat** : ce n'est pas une garantie formelle.
- **Bruit de Laplace** : simulation avec une borne pédagogique (`BORNE_MAX = 30`),
  ce n'est **pas** une implémentation complète de confidentialité différentielle.
- **Signature HMAC** : prouve l'origine des classifications, pas la confidentialité.
- **La fédération n'annule pas l'échange** : les classifications et les agrégats
  circulent réellement entre les nœuds.
- **Corrélation ≠ causalité** : les données fictives suggèrent une association, elles
  ne démontrent aucune relation médicale.

Un système réel exigerait : HTTPS, identités organisationnelles, autorisations
précises, journalisation des accès, gouvernance et analyse des risques de divulgation.

---

## 12. Support pédagogique

Le support complet des quatre TP (énoncé, code de référence, questions et résultats
attendus) est disponible dans [`docs/Support_TP1_TP4.pdf`](docs/Support_TP1_TP4.pdf).
