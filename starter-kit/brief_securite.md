Document transmis à l'étudiant par Thomas Verdier, en pièce jointe de son message.

<aside>
ℹ️

Bulle info : ce brief décrit ce que l'audit interne a trouvé et le risque associé à chaque constat. Il ne donne pas les corrections à appliquer : c'est à l'étudiant de les choisir et de les justifier.

</aside>

## Contexte de l'audit

L'audit interne a porté sur l'application de gestion des stations, des véhicules et des comptes des agents de terrain. Il a relevé des lacunes sur la protection des données des agents et sur le contrôle d'accès à l'application.

Le périmètre de ce brief s'arrête au code de l'application. Le déploiement, la supervision et la gestion des incidents ne sont pas concernés.

## Constats

### 1. Mots de passe stockés sans protection

Les mots de passe des agents sont conservés tels quels en base de données. Toute personne accédant à la base, ou à une sauvegarde, lit directement les identifiants des agents et peut les réutiliser ailleurs.

Fichiers concernés : `agents/models.py` (`Agent`), `agents/services.py` (`create_agent`, `change_password`), `core/seed.py`.

### 2. Absence de contrôle d'accès

Les points d'entrée de l'API répondent sans exiger d'identification. N'importe quelle requête atteignant le serveur peut consulter ou modifier les données des stations, des véhicules et des agents.

Fichiers concernés : `norlys_mobilite/settings.py` (`REST_FRAMEWORK`), `views.py` des applications `agents`, `stations` et `vehicles`.

### 3. Entrées non validées

Les données reçues par l'API ne sont pas systématiquement contrôlées avant traitement. Des valeurs incohérentes peuvent être enregistrées, et certaines provoquent des erreurs en chaîne côté serveur.

Fichiers concernés : `views.py` des applications `agents`, `stations` et `vehicles`.

### 4. Erreurs techniques exposées

En cas d'erreur, l'application renvoie des détails techniques internes. Ces messages renseignent un attaquant sur la structure de l'application et sur les technologies utilisées.

Fichiers concernés : `norlys_mobilite/settings.py` (`DEBUG`, `REST_FRAMEWORK`), `core/exceptions.py`.

### 5. Données exposées par les réponses de l'API

Les réponses de l'API sont construites directement à partir des objets de persistance. Elles livrent plus de champs que nécessaire, et parfois des données liées qui n'avaient pas à sortir.

Fichiers concernés : `serializers.py` des applications `agents`, `stations` et `vehicles`, `agents/views.py`.

## Ce qui est attendu

Pour chaque constat : une correction dans le code, un test qui prouve que le problème ne peut plus se reproduire, et une entrée dans le README indiquant ce que la faille permettait, la correction retenue et sa raison.

Chaque constat doit également être rattaché à la catégorie correspondante du Top 10 OWASP.

<aside>
⚠️

Bulle attention : la sécurisation modifie du code existant. Elle ne doit être entreprise qu'une fois la suite de tests en place et verte, faute de quoi les corrections casseront des comportements en silence.

</aside>