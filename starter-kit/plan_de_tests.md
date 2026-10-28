Document transmis à l'étudiant par Thomas Verdier, en pièce jointe de son message.

<aside>
ℹ️

Bulle info : ce plan dit ce qui doit être vérifié et à quel niveau. Il donne un exemple rédigé par niveau de test, pas la solution : les cas restants sont à écrire par l'étudiant.

</aside>

## Ce que ce plan couvre

L'application de Norlys Mobilité gère les stations, les véhicules et les comptes des agents de terrain. Les deux régressions parties en production venaient de règles métier modifiées sans filet. Le plan cible donc en priorité ces règles, puis les parcours qui les traversent.

Trois niveaux sont attendus :

- les tests unitaires, qui vérifient une règle métier isolément, sans base de données ni serveur ;
- les tests d'intégration, qui vérifient qu'un parcours traverse correctement les couches, jusqu'à la base ;
- un test end-to-end, qui rejoue un parcours complet tel qu'un agent le vivrait.

## Ce qui doit être vérifié

### Niveau unitaire

Pour chaque règle métier ciblée : le cas nominal, au moins un cas limite et au moins un cas d'erreur. Les dépendances de la classe testée sont remplacées par des doublures.

Une vingtaine de tests unitaires sont attendus, sur les règles suivantes :

- `vehicles/services.py` :
  - `start_rental` : véhicule `AVAILABLE`, rattaché à une station et chargé à au moins 20 % ;
  - `end_rental` : station active et non pleine, statut recalculé selon la batterie ;
  - `update_battery` : bascule entre `AVAILABLE` et `LOW_BATTERY` autour de 20 % (tester 19 et 20) ;
  - `assign_to_station` : refusée si la station est désactivée ou pleine, ou si le véhicule est `IN_USE` ou `OUT_OF_SERVICE`.
- `stations/services.py` :
  - `compute_occupancy` : places libres et taux d'occupation ;
  - `update_station` : la capacité ne descend jamais sous le nombre de véhicules présents ;
  - `deactivate_station` : uniquement si la station est vide ;
  - `assign_manager` : uniquement un superviseur actif.
- `agents/services.py` :
  - `create_agent` : identifiant obligatoire et unique, e-mail unique, rôle `FIELD` par défaut.

Exemple :

```python
def test_update_battery_switches_to_low_battery_below_threshold(mocker):
    # Préparation
    vehicle = Vehicle(id=1, status=Vehicle.Status.AVAILABLE, battery_level=50)
    get_vehicle = mocker.patch("vehicles.services.get_vehicle", return_value=vehicle)
    mocker.patch.object(Vehicle, "save")

    # Action
    result = update_battery(vehicle_id=vehicle.id, level=19)

    # Vérification
    get_vehicle.assert_called_once_with(vehicle_id=vehicle.id)
    assert result.status == Vehicle.Status.LOW_BATTERY
```

### Niveau intégration

Les parcours qui vont du point d'entrée de l'API jusqu'à la base de données, dont au moins un exécuté contre une base réelle éphémère plutôt que simulée.

Cinq parcours sont attendus :

- consulter l'occupation d'une station qui contient des véhicules : la réponse indique le nombre de places libres et le taux d'occupation ;
- affecter un véhicule à une station déjà pleine : l'affectation est refusée et le véhicule reste hors de la station. Ce test s'exécute sur une base PostgreSQL, le moteur de production, et non sur SQLite ;
- louer un véhicule puis le rendre dans une station : le véhicule quitte sa station pendant la location, puis y est rattaché au retour avec son nouveau niveau de batterie ;
- descendre la batterie d'un véhicule disponible sous 20 % : son statut passe à `LOW_BATTERY` en base ;
- créer un agent avec un identifiant déjà utilisé : la création est refusée et aucun second agent n'est enregistré.

Exemple :

```python
@pytest.mark.django_db
def test_low_battery_is_saved():
    # Préparation
    vehicle = Vehicle.objects.create(serial_number="V1", type=Vehicle.Type.BIKE, battery_level=80)

    # Action
    response = APIClient().put(f"/api/vehicles/{vehicle.id}/battery/", {"level": 19}, format="json")

    # Vérification
    assert response.status_code == 200
    vehicle.refresh_from_db()
    assert vehicle.status == Vehicle.Status.LOW_BATTERY
```

### Niveau end-to-end

Un parcours complet, de la première requête jusqu'au résultat attendu.

Créer une station de capacité 2, y ajouter un vélo chargé à 80 % et vérifier que son occupation est de 0.5 ; démarrer une location, puis rendre le vélo avec 12 % de batterie : il passe en `LOW_BATTERY` et une nouvelle location est refusée.

## Couverture attendue

Un rapport de couverture doit être généré sur le périmètre de ce plan, et commenté dans le README : ce que le chiffre dit, ce qu'il ne dit pas, et au moins une classe peu couverte assumée.

Au moins 80 % des lignes des modules `services.py`, couvertes par les seuls tests unitaires :

```bash
coverage run -m pytest -m "not django_db"
coverage report --include="*/services.py"
coverage html
```

Le rapport détaillé est dans `htmlcov/index.html`.

<aside>
⚠️

Bulle attention : un test sans assertion s'exécute, passe au vert et ne vérifie rien. Il augmente la couverture sans protéger l'application.

</aside>