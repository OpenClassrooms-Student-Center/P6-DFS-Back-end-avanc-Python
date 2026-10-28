# Norlys Mobilité — Gestion de flotte

Application interne de Norlys Mobilité pour la gestion des stations, des véhicules partagés (vélos et trottinettes) et des comptes des agents de terrain. Elle expose une API REST consommée par les outils de terrain et le back-office. Elle est construite avec Django et Django REST Framework, documentée en OpenAPI avec drf-spectacular.

## Prérequis

- Python 3.14 (`python --version`)
- `pip` et le module `venv` fournis avec Python
- PostgreSQL 16 (uniquement lorsque `DB_ENGINE=postgres` ; le développement local utilise SQLite)

## Installation

```bash
git clone <url-du-depot> norlys-mobilite
cd norlys-mobilite
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Les dépendances sont figées à une version exacte : `requirements.txt` contient celles de l'application, `requirements-dev.txt` y ajoute les outils de développement (black, ruff, pytest, coverage). La version minimale de Python est déclarée dans `pyproject.toml` (`requires-python`).

## Base de données : deux moteurs

Le projet fonctionne avec deux moteurs de base de données, sélectionnés par la variable `DB_ENGINE` du fichier `.env` :

- **SQLite** (par défaut) : la base est le fichier `db.sqlite3` à la racine du dépôt (non versionné). Rien à installer, adapté pour démarrer rapidement.
- **PostgreSQL 16** : le moteur de production. Il faut disposer d'un serveur PostgreSQL (conteneur Docker ou installation native, au choix) et d'une base accessible.

Pour changer de moteur, commenter un bloc et décommenter l'autre dans `.env` (voir `.env.example`). Les commandes de lancement sont identiques dans les deux cas.

## Lancement

```bash
python manage.py migrate
python manage.py seed
python manage.py createsuperuser
python manage.py runserver
```

L'application démarre sur `http://127.0.0.1:8000`, qui redirige vers Swagger UI. La commande `seed` insère un jeu de données de démarrage (agents, stations, véhicules) si la base est vide ; elle est facultative. La commande `createsuperuser` demande un identifiant et un mot de passe, puis crée le compte d'accès à l'administration Django.

L'administration Django permet de consulter et de modifier les données directement, sans client SQL. Elle écrit en base sans passer par les services : les règles de gestion n'y sont pas appliquées.

- Swagger UI : `http://127.0.0.1:8000/api/docs/`
- Schéma OpenAPI : `http://127.0.0.1:8000/api/schema/`
- Administration Django : `http://127.0.0.1:8000/admin/`

## Structure du projet

```
.
├── manage.py                    commandes Django
├── requirements.txt             dépendances de l'application, en version exacte
├── requirements-dev.txt         outils de développement (black, ruff, pytest, coverage)
├── pyproject.toml               métadonnées, version de Python, black, ruff
├── .env.example                 modèle du fichier .env (à copier)
├── AGENTS.md                    consignes pour les assistants de code
├── norlys_mobilite/             paquet projet
│   ├── settings.py              configuration (Django, DRF, drf-spectacular, bases)
│   ├── urls.py                  routage racine (/admin/, /api/…)
│   ├── asgi.py
│   └── wsgi.py
├── core/                        application transverse, sans modèle ni route
│   ├── apps.py                  déclaration de l'application
│   ├── exceptions.py            ResourceNotFoundError, BusinessRuleError, ConflictError
│   ├── seed.py                  jeu de données de démarrage
│   └── management/commands/     commande `seed`
├── agents/                      comptes des agents et superviseurs
├── stations/                    stations, capacité, responsable, occupation
└── vehicles/                    véhicules, location, batterie, maintenance
```

Chaque application Django (`agents`, `stations`, `vehicles`) suit la même organisation :

| Module           | Rôle                                                              |
|------------------|-------------------------------------------------------------------|
| `models.py`      | modèle de persistance et énumérations                             |
| `admin.py`       | enregistrement du modèle dans l'administration Django             |
| `tests/`         | tests de l'application                                            |
| `migrations/`    | migrations versionnées                                            |
| `selectors.py`   | fonctions de lecture, seul accès en lecture à l'ORM (convention du HackSoft Django Styleguide, équivalent de méthodes de QuerySet personnalisées) |
| `services.py`    | règles de gestion et écritures (la transaction est portée par la requête HTTP, `ATOMIC_REQUESTS`) |
| `serializers.py` | représentation JSON des réponses                                  |
| `views.py`       | vues `@api_view` : lecture de la requête, appel d'un service, réponse |
| `urls.py`        | routes de la ressource                                            |

`core` est aussi une application Django, mais sans modèle ni route : elle est installée pour que Django découvre la commande `seed`.

Flux d'une requête : en lecture, `vue` → `selectors` ; en écriture, `vue` → `service`, qui lit via les `selectors` et écrit via le `modèle`. Les règles de gestion vivent exclusivement dans les services ; une vue ne contient pas de logique. Les seuils métier (`MIN_BATTERY_FOR_RENTAL`, `MAX_BATTERY_LEVEL`) sont des constantes de `vehicles/models.py`.

## Règles de gestion principales

- L'identifiant d'un agent est obligatoire et unique ; son adresse e-mail, si elle est fournie, est unique. Sans rôle précisé, un agent est `FIELD`. Un mot de passe ne peut pas être vide. Un agent responsable d'une station ne peut pas être désactivé.
- Une station a une capacité strictement positive ; elle ne peut pas être réduite sous le nombre de véhicules présents, ni désactivée tant qu'elle contient des véhicules.
- Seul un agent actif ayant le rôle `SUPERVISOR` peut être désigné responsable d'une station.
- Un véhicule est louable s'il est `AVAILABLE`, rattaché à une station et que sa batterie est au moins à 20 %. En dessous de ce seuil il passe en `LOW_BATTERY`.
- Un véhicule ne peut être affecté qu'à une station active et non pleine ; un véhicule `IN_USE` ou `OUT_OF_SERVICE` ne peut pas être affecté.
- Le retour de location se fait dans une station active et non pleine ; il fixe le niveau de batterie et recalcule le statut (`AVAILABLE` ou `LOW_BATTERY`).
- Un véhicule `IN_USE` ne peut ni partir en maintenance ni être retiré de la flotte.

## Points d'entrée de l'API

L'API expose trois ressources : `/api/agents/`, `/api/stations/` et `/api/vehicles/`. Toutes les routes se terminent par un slash ; les corps de requête et de réponse sont en JSON, en `snake_case`.

Les routes, leurs paramètres et leurs schémas sont décrits dans Swagger UI (`/api/docs/`).

## Qualité du code

```bash
black .         # formate le code
ruff check .    # analyse statique
```

Les deux outils sont configurés dans `pyproject.toml`.

## Tests

```bash
pytest                   # lance la suite de tests
coverage run -m pytest   # lance la suite en mesurant la couverture
coverage html            # génère le rapport dans htmlcov/index.html
```

Les tests se placent dans le dossier `tests/` de chaque application. pytest et coverage sont configurés dans `pyproject.toml`.

## Licence

Logiciel propriétaire — usage interne Norlys Mobilité. Tous droits réservés.
