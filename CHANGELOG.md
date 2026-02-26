# Journal des modifications
## [3.2.4] - 2026-02-26
> Commit : `fix(ui): improve touch ergonomics for inputs, selects and admin buttons on 12-inch screen`
### Modifié
- `Styles/common.css` : padding de `input, select` augmenté de `0.5rem` à `0.75rem 1rem` pour des cibles tactiles confortables (~44px de hauteur totale) sur les pages prendre et ranger. Non appliqué aux filtres du tableau (leur règle spécifique dans `ecran.css` prend le dessus).
- `Styles/ecran.css` : ajout d'une règle `.export-btn, .purge-btn` avec `padding: 0.75rem 1.5rem` et `min-height: calc(44px + 1.5rem)` pour aligner leur hauteur sur celle des boutons d'action principaux (68px).

## [3.2.3] - 2026-02-26
> Commit : `fix(ui): normalize button height and text centering across all pages`
### Modifié
- `Styles/common.css` : `box-shadow` étendu aux `<button>` ; `display: flex; align-items: center; justify-content: center` ajouté pour centrer le texte ; `min-height` passé à `calc(44px + 1.5rem)` pour compenser le `box-sizing: border-box` natif de Chromium sur `<button>` et égaler la hauteur des éléments `<a>` (`content-box`).
- `Styles/index.css` : `.logout-button` passé en `display: flex; align-items: center; justify-content: center` pour centrer le texte verticalement ; `box-shadow`, `padding: 0.75rem 1rem` et `min-height: 44px` ajoutés. `.admin-link` et `.user-link` : `min-height: calc(44px + 1.5rem)` ajouté pour compenser le `box-sizing: border-box` explicite et uniformiser la hauteur avec les boutons de retour.
- `Styles/supprimer.css` : `box-shadow` ajouté à `.cancel-btn`.

## [3.2.2] - 2026-02-26
> Commit : `fix(ui): add outline shadow to navigation buttons for scroll visibility`
### Modifié
- `Styles/common.css` : ajout d'un `box-shadow` sur `.retour`, `.retour-menu`, `.admin-link`, `.user-link` pour les distinguer visuellement de l'arrière-plan lors du défilement.

## [3.2.1] - 2026-02-26
> Commit : `fix(ui): make index buttons full-width and remove simple back button from ajouter`
### Modifié
- `Styles/index.css` : `.admin-link` et `.user-link` passés en `display: flex; width: 100%` pour occuper toute la largeur du conteneur et assurer une harmonie visuelle cohérente.
- `Templates/ajouter.html` : suppression du bouton "Retour au menu" (lien `/index` sans fermeture de la DB), seul le bouton "Fermer connexion DB et retour au menu" reste présent.

## [3.2.0] - 2026-02-24
> Commit : `feat(ui): improve touch ergonomics for 12-inch touchscreen`
### Modifié
- `Styles/common.css` : padding des boutons augmenté (`0.85rem 1rem`) avec `min-height: 44px` pour respecter la taille minimale tactile recommandée.
- `Styles/common.css` : liens de navigation (`.admin-link`, `.retour`, `.retour-menu`) agrandis (`padding: 0.75rem 1.25rem`, `min-height: 44px`) pour des cibles tactiles plus accessibles.
- `Styles/ecran.css` : suppression de `touch-action: pan-y` sur la table pour permettre au JS de gérer le scroll dans les deux directions. Padding des boutons inline augmenté à `0.6rem 1rem`.
- `Styles/login.css` : conteneur de connexion passé de largeur fixe (`300px`) à fluid (`width: 90%; max-width: 360px`). Padding des boutons augmenté à `14px`.
- `Styles/prendre.css`, `ranger.css`, `supprimer.css`, `ajouterU.css` : conteneurs passés de largeur fixe (`400px`) à fluid (`width: 90%; max-width: 400px`).
- `Styles/supprimer.css` : `.cancel-btn` agrandie avec `min-height: 44px` pour uniformiser la taille tactile.
- `Styles/ajouterU.css` : checkbox "Admin" agrandie (`1.5rem × 1.5rem`) pour une utilisation tactile plus aisée.
- `Functions/ecranDrag.js` : réécriture complète — scroll 1 doigt via `scrollLeft`/`scrollTop`, ajout d'un handler `touchend` pour réinitialiser l'état, suppression du positionnement via CSS `transform`.
- `Templates/modifier.html` : remplacement du `alert()` JavaScript bloquant par une `<div class="error">` stylée, plus fiable en mode kiosque Chromium.
- `Templates/prendre.html` : suppression de l'attribut `autofocus` pour éviter l'ouverture automatique du clavier virtuel à l'arrivée sur la page.
- `Templates/supprimer.html` : correction de l'attribut `lang="en"` en `lang="fr"`.

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
