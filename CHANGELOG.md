# Journal des modifications
## [3.6.1] - 2026-02-26
> Commit : `fix(ajouter): switch export to XLSX, use positional column mapping on import, match button style`
### Modifié
- `APP.py` : `_parse_import_file()` — mapping désormais par **position de colonne** (la première ligne est ignorée comme en-tête ; l'ordre attendu est `ref_ecran, libelle, pcb, fab, n_fab, type, n`). Route `/export_serigraphie` — export au format `.xlsx` (openpyxl) à la place du CSV.
- `Templates/ajouter.html` : libellé du bouton "Exporter CSV" → "Exporter".
- `Styles/ajouter.css` : `.ie-btn` reprend le style visuel des boutons `.retour` (fond jaune `#feed00`, texte sombre, gras, `border-radius: 4px`, même double ombre).
- `tests/web/test_import_export.py` : tests d'export mis à jour pour vérifier le format XLSX et les en-têtes de colonnes en ordre positionnel.

## [3.6.0] - 2026-02-26
> Commit : `feat(ajouter): add CSV export and CSV/XLSX import with conflict resolution`
### Ajouté
- `APP.py` : helper `_parse_import_file()` acceptant `.csv` et `.xlsx`. Route `GET /export_serigraphie` : export de la table `serigraphie` en CSV téléchargeable. Route `POST /import_serigraphie` : import d'un fichier CSV ou XLSX — insertion directe des nouvelles lignes, affichage de la page de résolution pour les conflits (ref_ecran déjà existant). Route `POST /import_serigraphie/confirm` : application des choix (garder / écraser par ligne, ou écraser tout).
- `Templates/import_conflicts.html` : page de comparaison côte à côte (en base vs fichier importé) avec checkbox par ligne et bouton "Écraser tout".
- `Styles/import_conflicts.css` : styles de la page de résolution des conflits.
- `Templates/ajouter.html` : barre de deux boutons "Exporter CSV" et "Importer" en haut à gauche, avec formulaire d'upload masqué soumis automatiquement à la sélection du fichier.
- `Styles/ajouter.css` : styles `.ie-bar` et `.ie-btn` pour la barre import/export.
- `tests/web/test_import_export.py` : 13 tests couvrant export, import CSV, import XLSX, gestion des conflits et résolution.
- `requirements.txt` : ajout de `openpyxl`.

## [3.5.4] - 2026-02-26
> Commit : `fix(ui): match washing panel width to main container and add item separators`
### Modifié
- `Styles/index.css` : `.laver-actions` passe de `width: fit-content` à `width: 400px; max-width: 400px` (même largeur que le container principal). `.laver-info` — ajout de `flex: 1` et `word-break: break-word` pour le retour automatique à la ligne. Ajout de `.laver-sep` : ligne fine centrée à 60% de largeur entre chaque item.
- `Templates/index.html` : ajout d'un `<div class="laver-sep">` entre chaque item de la liste (via `{% if not loop.last %}`).

## [3.5.3] - 2026-02-26
> Commit : `fix(ui): make washing panel self-contained with rounded corners and auto width`
### Modifié
- `Templates/index.html` : suppression du modificateur `page-wrapper--with-laver` (devenu inutile).
- `Styles/index.css` : `.page-wrapper` — ajout de `gap: 1rem` entre les containers. `.laver-actions` — passe en `width: fit-content; min-width: 220px` (s'adapte au contenu), `border-radius: 8px` (coins arrondis), `border: 1px solid #FF4C4C`, `box-shadow` propre ; suppression de `align-self: stretch`, `border-left/right` et `width: 260px`. `.laver-info` — suppression de `flex: 1` et `word-break` devenus inutiles. Suppression des règles `.page-wrapper--with-laver`.

## [3.5.2] - 2026-02-26
> Commit : `fix(ui): dock washing panel flush to the left of the main container`
### Modifié
- `Templates/index.html` : introduction d'un `div.page-wrapper` (avec modificateur `--with-laver`) enveloppant le panneau lavage et le container principal, rendant les deux blocs contigus dans un layout flex.
- `Styles/index.css` : `.laver-actions` passe d'un positionnement absolu à un élément flex (`align-self: stretch`, `border-left: 4px solid #FF4C4C`, `border-right: 1px solid #2A2D46`, fond `#191B2A`). `.page-wrapper--with-laver` applique `overflow: hidden` + `border-radius: 8px` + `box-shadow` pour unifier visuellement les deux blocs. `.form-container` est élargi à `width: 400px` et son ombre supprimée dans ce contexte.

## [3.5.1] - 2026-02-26
> Commit : `fix(ui): move washing section outside main container on index page`
### Modifié
- `Templates/index.html` : la section "Écrans à laver" est déplacée hors du `.form-container` (au niveau du `<body>`).
- `Styles/index.css` : `.laver-actions` passe en `position: absolute; top: 1rem; left: 1rem; width: 260px` avec `max-height` et scroll vertical — le container principal reste centré indépendamment. `body` passe en `position: relative` pour contenir le bloc absolu.

## [3.5.0] - 2026-02-26
> Commit : `feat(logs): track who returns and washes screens in sortie_logs`
### Ajouté
- `database/schema.sql` : colonne `personne_rangement TEXT` ajoutée à `sortie_logs` — enregistre qui a rangé ou lavé l'écran.
- `APP.py` : migration automatique dans `_ensure_log_tables()` — ajout de `personne_rangement` via `ALTER TABLE` sur les bases existantes (vérification via `PRAGMA table_info`).
- `APP.py` : `_sync_daily_log()` inclut désormais `personne_rangement` dans le SELECT et dans les CSV exportés (nouvelle colonne entre `personne` et `heure_sortie`).
- `APP.py` : route `/ranger` — `personne_rangement` est renseigné avec `session['prenom']` lors de la mise à jour de `sortie_logs`.
- `APP.py` : route `/laver` — `personne_rangement` est renseigné avec `session['prenom']` lors de la mise à jour de `sortie_logs`.
### Modifié
- `tests/web/test_workflow_ecrans.py` : mise à jour des assertions CSV pour refléter le nouvel en-tête et la nouvelle colonne `personne_rangement`.
- `tests/system/test_logs_utils.py` : mise à jour des assertions CSV pour refléter le nouvel en-tête et la nouvelle colonne `personne_rangement`.

## [3.4.0] - 2026-02-26
> Commit : `feat(laver): add washing management section on index page`
### Ajouté
- `APP.py` : route `/laver` (POST, tous utilisateurs connectés) — vérifie que l'écran est rentré et non lavé (`sorti=0, lave=0`), met à jour `serigraphie.lave = 1`, met à jour `sortie_logs.lavee = 1` sur la dernière entrée de retour correspondante, puis synchronise le CSV journalier.
- `APP.py` : la route `/index` récupère désormais la liste des écrans à laver (`sorti=0, lave=0`) et la transmet au template.
- `Templates/index.html` : section "Écrans à laver" affichant, pour chaque écran concerné, sa référence, son libellé, son emplacement et un bouton "Laver" qui poste vers `/laver`.
- `Styles/index.css` : styles `.laver-actions`, `.laver-item`, `.laver-info`, `.laver-btn` pour la section de lavage (bordure rouge, bouton bleu, ergonomie tactile 44 px).
- `tests/web/test_laver.py` : 8 tests couvrant accès non connecté, marquage lavé, mise à jour des logs, cas limites (déjà lavé, sorti, sans entrée de log), et affichage conditionnel sur `/index`.

## [3.3.0] - 2026-02-26
> Commit : `feat(stats): add admin statistics page for screen usage`
### Ajouté
- `APP.py` : nouvelle route `/stats` (admin uniquement) — agrège les passages par écran via `sortie_logs` (LEFT JOIN sur `serigraphie`) et les passages par personne, transmet les résultats au template.
- `Templates/stats.html` : page affichant le total des passages, un tableau "écrans les plus utilisés" (réf., libellé, fab, type, compteur) et un tableau "personnes les plus actives".
- `Styles/stats.css` : styles dédiés à la page stats (tableau, badge total, surbrillance du premier résultat).
- `Templates/index.html` : lien "Statistiques" ajouté dans la section administration.
- `tests/web/test_stats.py` : couverture de la route `/stats` (accès non connecté, non admin, accès admin, comptage de passages, affichage du total).

## [3.2.5] - 2026-02-26
> Commit : `fix(ui): unify red button style across all pages`
### Modifié
- `Styles/login.css` : `.shutdown-button` — couleur `#d9534f` → `#FF4C4C`, hover `#c9302c` → `#E04343`.
- `Styles/supprimer.css` : `.confirmer` — couleur `#F44336` → `#FF4C4C`, `color: #FFFFFF` ajouté, hover `#b63127` → `#E04343`.
- `Styles/ecran.css` : `.purge-btn` — couleur `#721c24` → `#FF4C4C`, `color: #FFFFFF` ajouté, `border` supprimé, hover `#a71d2a` → `#E04343`.

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
