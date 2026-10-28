# Guide pour les assistants IA intervenant sur ce dépôt

Ce fichier s'adresse aux assistants de code intégrés à l'éditeur. Il décrit la posture attendue, le projet, sa stack et les conventions à respecter.

## Posture

- **Aider à comprendre avant de produire.** Quand une demande porte sur du code, commence par expliquer le mécanisme en jeu (ce que fait un décorateur, pourquoi un module existe, ce qu'un test vérifie), puis propose du code.
- **Procéder par petites étapes.** Une modification à la fois, exécutée et vérifiée, plutôt qu'un grand bloc livré d'un coup.
- **Poser des questions avant de coder.** Si l'objectif, le périmètre ou le niveau attendu n'est pas clair, demande. Ne présume pas.
- **Laisser les décisions au développeur.** Quand plusieurs approches sont possibles, présente-les avec leurs conséquences ; c'est lui qui tranche et qui devra justifier le choix.
- **Ne pas contourner un problème.** Une exception, un test qui échoue ou un comportement inattendu s'expliquent. Propose un diagnostic, pas un pansement.

## Le projet

Application interne de Norlys Mobilité : gestion des stations, des véhicules partagés (vélos, trottinettes) et des comptes des agents de terrain, exposée via une API REST sous `/api/`.

### Stack

| Composant             | Version |
|-----------------------|---------|
| Python                | 3.14    |
| Django                | 6.1     |
| Django REST Framework | 3.18    |
| drf-spectacular       | 0.30 (documentation OpenAPI sur `/api/docs/`) |
| psycopg               | 3.3 (PostgreSQL, `DB_ENGINE=postgres`) |
| python-dotenv         | 1.2 (lecture de `.env`) |
| SQLite                | base de développement par défaut |

Le projet vise ces versions ; les versions exactes sont figées dans `requirements.txt` (application) et `requirements-dev.txt` (outils de développement : black, ruff, pytest, pytest-django, pytest-mock, coverage). Ne propose pas d'API dépréciées ni de syntaxe antérieure à Python 3.14.

### Architecture

```
norlys_mobilite/   settings, urls racine, asgi, wsgi
core/              app sans modèle ni route : exceptions métier (ResourceNotFoundError, BusinessRuleError, ConflictError pour les doublons), données de démarrage, commande `seed`
agents/            \
stations/           > une application Django par ressource
vehicles/          /
```

Chaque application contient `models.py`, `admin.py`, `migrations/`, `selectors.py` (fonctions de lecture, convention du HackSoft Django Styleguide, à préférer ici aux QuerySets personnalisés), `services.py` (règles de gestion et écritures), `serializers.py`, `views.py` (fonctions `@api_view`) et `urls.py`.

Flux : en lecture, `vue` → `selectors` ; en écriture, `vue` → `service`, qui lit via les `selectors` et écrit via le `modèle`. Toute règle métier vit dans un service. Une vue lit la requête, appelle un selector ou un service et sérialise le résultat ; elle ne décide de rien.

Points notables du code :

- Les services sont des fonctions module-level qui importent nominativement leurs dépendances (`get_station`, `get_vehicle`, `get_agent`, `count_vehicles_in_station`, `serial_number_exists`, `is_station_manager`…). Ce sont ces noms, dans le module du service, qu'on remplace par des doublures pour tester une règle isolément.
- Le nombre de véhicules d'une station se calcule par `vehicles.selectors.count_vehicles_in_station`, pas par une relation inverse (les `ForeignKey` ont `related_name="+"`).
- Les seuils métier sont des constantes de `vehicles/models.py` (`MIN_BATTERY_FOR_RENTAL`, `MAX_BATTERY_LEVEL`) ; `Vehicle.status_for_battery` et `Station.has_free_slot` sont des méthodes pures.
- Les vues distinguent les méthodes avec `match request.method` sur `http.HTTPMethod` ; une méthode non listée dans `@api_view` reçoit un 405 de DRF avant d'entrer dans la fonction. Chaque vue porte un `@extend_schema` qui la documente dans Swagger sans rien valider.
- Les données de démarrage sont insérées par `core.seed.seed_if_empty`, appelé uniquement par la commande `python manage.py seed` : une base créée par `migrate`, y compris une base de test, reste vide.

## Conventions et bonnes pratiques Django / DRF à rappeler

Python vise la lisibilité avant la déclaration. Un conseil qui réclame une interface ou une classe abstraite pour chaque service est importé d'ailleurs.

- **Environnement virtuel.** Toujours travailler dans `.venv` ; installer dans le Python du système rend le projet non reproductible.
- **Découpage par le cadre.** Respecter les modules de chaque application. Une règle de gestion dans une vue marche, et devient intestable dès qu'il faut la vérifier sans requête HTTP.
- **Validation des entrées.** Dans un projet DRF, elle se déclare dans un sérialiseur (`validators`, `validate_<champ>`, `serializer.is_valid(raise_exception=True)`), là où la donnée entre, plutôt qu'avec des `if` en tête de vue ou des `int(...)` nus.
- **Gestion des erreurs.** Une exception métier est une classe ; le `EXCEPTION_HANDLER` de DRF la traduit en réponse HTTP. Une réponse d'erreur destinée à un client ne contient ni traceback ni détail d'implémentation ; `DEBUG` ne vaut jamais `True` hors d'un poste de développement.
- **Exposition de l'API.** Lister explicitement les champs d'un `ModelSerializer` plutôt que `fields = "__all__"` : un modèle qui traverse la vue sans filtre expose tout, y compris ce qu'on ajoutera demain, et les sérialiseurs imbriqués propagent l'exposition.
- **ORM.** Une relation chargée ligne par ligne est un N+1 ; `select_related` (clés étrangères) et `prefetch_related` (collections) le corrigent. Il ne se voit pas sur huit lignes et s'effondre sur mille.
- **Migrations.** Toujours committées, jamais générées deux fois pour le même changement.
- **Tests (pytest).**
  - `mocker.patch("module.du.service.nom_importe")` remplace une dépendance là où le service la voit ; une instance de modèle se construit avec `Model(...)` sans base, en patchant `save` si besoin. Un test qui vérifie une règle de calcul n'a pas besoin de `django_db`. Les services ne portent pas de `transaction.atomic` (la transaction est ouverte par requête HTTP, `ATOMIC_REQUESTS`) : ne pas en rajouter, sinon un test unitaire ouvrirait une connexion à la base.
  - `pytest-django` et `APIClient` traversent les couches jusqu'à une vraie base éphémère : réservés aux tests d'intégration et end-to-end, de préférence sur le même moteur que la production.
  - `django_assert_num_queries` compte les requêtes d'un parcours.
  - un test se structure en préparation / action / vérification et comporte au moins une assertion ; un test sans assertion couvre des lignes sans rien vérifier ;
  - `coverage.py` mesure ce qui est exécuté, pas ce qui est vérifié.
- **Sécurité.** Les mots de passe se stockent hachés par Django (`make_password`, `set_password`, `check_password`), jamais en clair. L'accès à une API se protège par des classes d'authentification et des permissions (`IsAuthenticated`) déclarées dans `REST_FRAMEWORK` ou par vue. Authentification (qui es-tu) et autorisation (que peux-tu faire) sont deux questions distinctes.
- **Style.** `black` formate, `ruff` signale ; un désaccord de style se règle par l'outil. Annotations de type encouragées sur les signatures publiques, pas exigées partout. Les appels aux fonctions du projet passent leurs arguments par nom (`get_vehicle(vehicle_id=vehicle_id)`) ; une condition écrit ce qu'elle teste (`len(value.strip()) == 0` plutôt que `not value.strip()`).

## Mises en garde

- **Secrets.** Ne jamais écrire de mot de passe, de clé ou de jeton dans le code, les settings versionnés ou un exemple de commande. Les valeurs réelles vont dans `.env` (ignoré par git) ; `.env.example` ne contient que des noms de variables et des valeurs factices.
- **Code généré.** Tout code produit par un assistant est une proposition à relire, exécuter et tester. Ne présente jamais une suggestion comme vérifiée si elle ne l'a pas été.
- **Données des agents.** Les comptes des agents (identifiants, contacts, mots de passe) sont des données personnelles. Ne les recopie pas dans des exemples, des logs ou des messages de commit, et signale toute manipulation qui les exposerait.
- **Périmètre.** Reste dans le code de l'application. Le déploiement, la supervision et l'infrastructure ne relèvent pas de ce dépôt.
