# Journal des modifications

## [2.1.4] - 2025-12-20
### Modifié
- Séparation du script `Demarrage_selection_branche.bat` en deux phases : la sélection de branche reste interactive (fenêtre persistante) puis relance automatiquement l'exécution standard avec la branche choisie afin que la fenêtre se referme ensuite, comme demandé.

## [2.1.3] - 2025-12-19
### Corrigé
- Fiabilisation de la sélection de branche dans `Demarrage_selection_branche.bat` (boucles `goto` explicites plutôt que blocs imbriqués) pour éviter les erreurs « . était inattendu » et garantir l'affichage des invites.

## [2.1.2] - 2025-12-18
### Corrigé
- Lancement via double-clic maintient désormais la console ouverte (le script se relance automatiquement dans une session `cmd /k`), garantissant l'affichage des invites de saisie.

## [2.1.1] - 2025-12-17
### Corrigé
- `Demarrage_selection_branche.bat` redemande maintenant le nom d'une branche si la liste distante n'est pas disponible, évitant la fermeture immédiate du script au double-clic.

## [2.1.0] - 2025-12-16
### Modifié
- Le script Windows `Demarrage_selection_branche.bat` affiche désormais les branches numérotées et permet de sélectionner la branche cible en saisissant son numéro plutôt que le nom complet.

## [2.0.0] - 2025-12-16
### Ajouté
- Script d'initialisation `scripts/init_db.py` et schéma partagé pour générer localement la base SQLite.
- Documentation enrichie pour détailler la structure du projet, la configuration multiplateforme et les commandes d'exécution.
### Modifié
- Suppression des artefacts locaux (venv, `armoire.db`, caches) du dépôt et introduction d'un `.gitignore` exhaustif.
- Modernisation d'`APP.py` (variables d'environnement, configuration générique, vérifications runtime) et mise à jour des scripts de déploiement Linux/Windows pour produire des installations reproductibles.

## [1.0.0] - 2025-08-27
### Ajouté
- Publication initiale du projet.
- Ajout de la licence MIT.
- Documentation et guide de contribution
