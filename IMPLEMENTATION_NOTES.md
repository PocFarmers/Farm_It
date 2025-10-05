# Implémentation de la Génération de Parcelles basée sur GeoJSON et TIF

## Résumé

Le système a été modifié pour générer les parcelles de jeu basées sur les coordonnées réelles des fichiers GeoJSON et les données des fichiers TIF (température et humidité du sol).

## Fichiers Modifiés

### Backend

1. **`back/geojson_handler.py`** (NOUVEAU)
   - Module pour charger et traiter les fichiers GeoJSON
   - Fonctions pour extraire les bounds, créer des grilles de points
   - Configuration des zones disponibles avec mapping GeoJSON/TIF

2. **`back/tif_handler.py`** (MODIFIÉ)
   - Ajout de `extract_tif_value_at_point()` : Extrait la valeur TIF à un point géographique
   - Ajout de `get_temperature_at_point()` : Récupère la température en °C à un point
   - Ajout de `get_soil_moisture_at_point()` : Récupère l'humidité du sol (0-1) à un point
   - Ajout de `get_tif_bounds_for_zone()` : Récupère les bounds du fichier TIF d'une zone

3. **`back/crud.py`** (MODIFIÉ)
   - `create_game_state()` prend maintenant un paramètre `zone_key` ('paris', 'amazon', 'biskra', 'kinshasa')
   - Génère les parcelles basées sur les bounds des fichiers TIF
   - Extrait les données de température et humidité pour chaque parcelle
   - Fonction legacy `create_game_state_legacy()` conservée en fallback

4. **`back/main.py`** (MODIFIÉ)
   - L'endpoint POST `/api/game` accepte maintenant un paramètre `zone_key`
   - Par défaut : `zone_key='paris'`

## Zones Disponibles

| Zone Key | Zone ID | Nom | Région | TIF Prefix | Bounds (température) |
|----------|---------|-----|--------|------------|---------------------|
| `paris` | temperate | Paris (Temperate) | Allemagne | tempere | lng [8.57, 11.42], lat [47.55, 49.45] |
| `amazon` | tropical | Amazon Central (Tropical) | Congo | tropicale | lng [19.05, 20.95], lat [-0.95, 0.95] |
| `biskra` | arid | North Africa Biskra (Arid) | Sahara | aride | lng [23.97, 26.02], lat [22.05, 23.95] |
| `kinshasa` | tropical | Kinshasa-Brazzaville (Tropical) | Congo | tropicale | lng [15.06, 15.65], lat [-4.46, -3.96] |

## Fonctionnement

### Création d'une Partie

```python
# Créer une partie pour la zone de Paris
game = crud.create_game_state(db, zone_key='paris')
```

### Processus

1. **Chargement de la configuration de zone**
   - Récupère zone_id, tif_prefix, et autres métadonnées

2. **Génération de la grille**
   - Utilise les bounds du fichier TIF de température
   - Crée une grille régulière avec `grid_size=0.05` (environ 5km)
   - Limite à 50 parcelles aléatoires

3. **Extraction des données TIF**
   - Pour chaque point de la grille :
     - Extrait la température du fichier TIF correspondant
     - Extrait l'humidité du sol (si disponible)

4. **Création des parcelles**
   - Type : 70% field, 30% forest (aléatoire)
   - Ownership : Les 3 premières parcelles sont possédées par le joueur

## Limitations Actuelles

### 1. Fichiers d'humidité du sol
- **Problème** : Tous les fichiers d'humidité couvrent la même zone (Kinshasa : lng [15.01, 15.65], lat [-4.46, -3.96])
- **Impact** : L'humidité n'est disponible que pour la zone Kinshasa
- **Solution actuelle** : Retourne `None` pour les autres zones, le game_logic utilise les valeurs par défaut

### 2. GeoJSON vs TIF
- **Problème** : Les fichiers GeoJSON ne correspondent pas géographiquement aux fichiers TIF
- **Solution** : Les parcelles sont générées basées sur les bounds des TIF, les GeoJSON sont ignorés pour la génération

## Tests

### Script de test
```bash
cd back
source venv/bin/activate
python test_parcel_generation.py
```

### Résultats
✅ Génération de 50 parcelles pour chaque zone
✅ Coordonnées basées sur les bounds réels des TIF
✅ Extraction de température fonctionnelle
⚠️ Extraction d'humidité limitée à la zone Kinshasa

## API

### Créer une partie
```
POST /api/game?zone_key=paris
```

**Paramètres** :
- `zone_key` (optionnel) : 'paris', 'amazon', 'biskra', 'kinshasa' (défaut: 'paris')

**Réponse** :
```json
{
    "id": 1,
    "current_stage": 0,
    "shovels": 10,
    "water_drops": 10,
    "score": 0,
    "parcels": [...]
}
```

## Améliorations Futures

1. **Fichiers d'humidité** : Obtenir des fichiers TIF d'humidité correspondant à chaque zone climatique
2. **Grille adaptative** : Ajuster `grid_size` en fonction de la taille de la zone
3. **Visualisation** : Aligner les GeoJSON avec les zones TIF réelles
4. **Cache** : Mettre en cache les données TIF pour améliorer les performances
5. **Validation** : Vérifier la cohérence des données TIF au démarrage de l'application

## Dépendances Ajoutées

```bash
pip install shapely
```

Ajoutée pour le traitement géospatial (intersections polygon, point-in-polygon, etc.)
