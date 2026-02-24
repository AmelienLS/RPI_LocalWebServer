# Journal des modifications
## [3.1.0] - 2026-02-24
> Commit : `chore(linux): revamp setup scripts with distro detection and graceful shutdown`
### Ajouté
- `Setups Linux/demarrage_release.sh` : clone la branche Release depuis GitHub, configure le venv, initialise la base de données si absente, puis lance l'application via gunicorn.
- `Setups Linux/demarrage_branche.sh` : liste les branches distantes, permet d'en sélectionner une, puis effectue le même flux que demarrage_release.sh.
- `Setups Linux/purge.sh` : arrête gunicorn si actif et supprime le répertoire d'installation complet pour revenir à un état propre.
- `Setups Linux/arreter.sh` : arrête proprement gunicorn via SIGTERM, attend la fin des requêtes en cours, et bascule sur SIGKILL si le délai de 15 secondes est dépassé. Dispose d'un fallback par recherche de processus si le fichier PID est absent.
### Modifié
- Anciens scripts Linux déplacés dans `Setups Linux/Legacy/` (Setup_release.sh, DémarrageTest.sh, purge.sh, Firefox_autostart.sh).
- Les nouveaux scripts détectent automatiquement la distribution (Ubuntu/Debian, Fedora standard, Fedora Silverblue/Kinoite) et adaptent l'installation des prérequis en conséquence.
- `demarrage_release.sh` et `demarrage_branche.sh` : ajout de l'option `--pid` à gunicorn pour écrire le PID dans `.gunicorn.pid`.

## [3.0.0] - 2025-12-17
### Ajouté
- Traçabilité quotidienne des écrans : table `sortie_logs`, génération automatique d'un CSV `JJ-MM-AAAA` par jour (avec référence, utilisateur, heures de sortie/rangement et statut de lavage).
- Variables d'environnement testées/overridables pour cibler le dossier de journaux (`APP_LOGS_DIR`) et nouvelles suites Pytest couvrant la génération de ces fichiers.
- Action d'export administrateur qui regroupe tous les journaux CSV dans une archive ZIP téléchargeable depuis `/ecran`.
- Bouton “Vider les journaux” : exporte puis supprime tous les CSV pour remettre le dossier de logs à blanc après archivage.
### Modifié
- Les routes `/prendre` et `/ranger` publient désormais chaque événement dans la table de logs puis régénèrent le fichier du jour, garantissant l'historique même si un écran est rangé un autre jour.

## [2.2.0] - 2025-12-17
### Ajouté
- Suites Pytest couvrant l'authentification, les flux d'ajout/prise/rangement ainsi que les scripts CLI et le schéma SQLite (répertoires `tests/web`, `tests/db`, `tests/scripts`).
- Tests front-end Vitest/JSDOM pour la logique de filtrage `Functions/Ecran.js` (`tests/js`).
### Modifié
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
