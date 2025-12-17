# Journal des modifications
## [3.0.0] - 2025-12-17
### Ajouté
- Traçabilité quotidienne des écrans : table `sortie_logs`, génération automatique d'un CSV `JJ-MM-AAAA` par jour (avec référence, utilisateur, heures de sortie/rangement et statut de lavage).
- Variables d'environnement testées/overridables pour cibler le dossier de journaux (`APP_LOGS_DIR`) et nouvelles suites Pytest couvrant la génération de ces fichiers.
- Action d'export administrateur qui regroupe tous les journaux CSV dans une archive ZIP téléchargeable depuis `/ecran`.
### Modifié
- Les routes `/prendre` et `/ranger` publient désormais chaque événement dans la table de logs puis régénèrent le fichier du jour, garantissant l'historique même si un écran est rangé un autre jour.
- `README.md` décrit la nouvelle fonctionnalité (format des fichiers, configuration, archivage).

## [2.2.0] - 2025-12-17
### Ajouté
- Suites Pytest couvrant l'authentification, les flux d'ajout/prise/rangement ainsi que les scripts CLI et le schéma SQLite (répertoires `tests/web`, `tests/db`, `tests/scripts`).
- Tests front-end Vitest/JSDOM pour la logique de filtrage `Functions/Ecran.js` (`tests/js`).
### Modifié
- Documentation `README.md` mise à jour avec les instructions détaillées pour exécuter les tests Python et JavaScript.
- `requirements.txt` inclut désormais `pytest` afin que les environnements CI et locaux disposent automatiquement du runner de tests.

## [2.1.1] - 2025-12-16
### Modifié
- Le script Windows se ferme automatiquement après l'exécution (et à l'arrêt du serveur) lorsque la branche a été choisie, en supprimant la pause finale hors mode interactif.

## [2.1.0] - 2025-12-16
### Corrigé
- `Demarrage_selection_branche.bat` redemande maintenant le nom d'une branche si la liste distante n'est pas disponible, évitant la fermeture immédiate du script au double-clic.

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
