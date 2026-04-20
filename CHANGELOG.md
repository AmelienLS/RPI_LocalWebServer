# Journal des modifications
## [4.0.2] - 2026-04-20
> Commit : `fix(index): shorten footer commit label to five characters`
### Modifié
- `Templates/index.html` : le label de version en bas de page affiche désormais uniquement les 5 premiers caractères de `commit` (au lieu du libellé complet), pour garder un footer court et lisible.

## [4.0.1] - 2026-04-20
> Commit : `fix(gerer-ecrans): allow scrolling in screen detail panel`
### Corrigé
- `Templates/gererE.html` + `Styles/gererE.css` : la fiche écran à droite est maintenant scrollable quand son contenu dépasse la hauteur disponible, ce qui rend toujours accessibles les boutons `Modifier` et `Supprimer`.

## [4.0.0] - 2026-04-20
> Commit : `feat(ui): complete dark design system redesign across all templates`
### Ajouté
- Nouveau système de design tokens CSS complet (`--bg`, `--surface`, `--elevated`, `--border`, `--accent`, `--success`, `--error`, `--warning`, `--blue`, etc.).
- Polices IBM Plex Sans + IBM Plex Mono intégrées via Google Fonts.
- Composants partagés dans `common.css` : `topbar`, `two-col`, `card`, `field-row`, `tag`, `alert-banner`, `action-card`, `action-row`, `empty-state`, variantes de boutons ghost (jaune, rouge, bleu, secondaire, sm).
- Layout non-admin centré sur `index.html` (`.one-col` + `.col-center`).
- Panneau détail utilisateur JS-driven dans `gererU.html` (sélection sans rechargement de page).
- Boutons de rôle visuels (Utilisateur / Administrateur) dans `ajouterU.html` et `modifierU.html`.
- Boutons Lavé / Non lavé visuellement sélectionnables dans `ranger.html`.
- Bouton "← Menu" en style ghost jaune sur toutes les pages avec TopBar.
### Modifié
- Tous les templates (`login`, `setup`, `index`, `prendre`, `ranger`, `ecran`, `gererE`, `gererU`, `stats`, `ajouter`, `modifier`, `ajouterU`, `modifierU`, `supprimer`) refondus avec le nouveau système de design.
- `APP.py` : correction de la détection du rôle admin (`request.form.get('admin') == 'on'` au lieu de `'admin' in request.form`) pour les routes d'ajout et de modification d'utilisateur.
- Boutons "← Menu" et "Déconnexion" alignés en taille avec les boutons principaux (`padding: 18px 20px`, `font-size: 16px`).
- Tous les placeholders de type "ex : ..." supprimés des champs de saisie, placeholders descriptifs conservés.
### Corrigé
- `index.html` : `{% endif %}` manquant sur le bloc `{% if a_laver or sortis_longtemps %}` causant une `TemplateSyntaxError`.
- Espacement entre les éléments de formulaire uniformisé via la règle `card-body > form { display:flex; flex-direction:column; gap:14px }`.
- Colonne admin non-admin retirée du DOM pour les utilisateurs standard (n'était plus cachée via CSS mais toujours présente).

## [3.23.0] - 2026-04-20
> Commit : `feat(ui): apply new dark design system to all templates and styles`
### Modifié
- `Styles/common.css` : refonte complète — nouvelles design tokens CSS (`--bg`, `--surface`, `--elevated`, `--border`, `--accent`, etc.), polices IBM Plex Sans + IBM Plex Mono via Google Fonts, nouveau système de layout (`page-screen`, `topbar`, `two-col`, `col-left`, `col-right`), composants partagés (`card`, `field-row`, `tag`, `alert-banner`, `action-card`, `empty-state`, boutons variantes).
- `templates/login.html` + `Styles/login.css` : layout centré avec icône, card, bouton Éteindre rouge.
- `templates/setup.html` : même pattern centré, boutons Nouvelle DB et Éteindre côte à côte.
- `templates/index.html` + `Styles/index.css` : header avec nom utilisateur et bouton déconnexion, layout 2 colonnes — alertes + action cards (Prendre/Ranger) + rangée Voir tous les écrans à gauche, grille admin 2×2 à droite.
- `templates/prendre.html` + `Styles/prendre.css` : TopBar, layout 2 colonnes — saisie ref à gauche, résultat avec emplacement en grand vert à droite.
- `templates/ranger.html` + `Styles/ranger.css` : TopBar, layout 2 colonnes — filtre + select + boutons Oui/Non + action à gauche, confirmation à droite. Boutons Lavé/Non lavé visuellement sélectionnables.
- `templates/ecran.html` + `Styles/ecran.css` : TopBar avec actions admin (Exporter/Vider), barre de filtre global, table sticky-header avec tags colorés (Lavé, Sorti, type), barre de statut en bas.
- `templates/gererE.html` + `Styles/gererE.css` : TopBar + bouton Ajouter, layout 2 colonnes — recherche à gauche, fiche détail avec field-rows + actions Modifier/Supprimer à droite.
- `templates/gererU.html` + `Styles/gererU.css` : TopBar + bouton Ajouter, layout 2 colonnes — liste cliquable à gauche, panneau détail JS-driven à droite (sélection sans rechargement).
- `templates/stats.html` + `Styles/stats.css` : TopBar, layout 2 colonnes — filtres période + total + classement personnes à gauche, classement écrans à droite.
- `templates/ajouter.html` + `Styles/ajouter.css` : TopBar avec Exporter/Importer, layout 2 colonnes avec grille de champs.
- `templates/modifier.html` : layout 2 colonnes, réutilise `ajouter.css`.
- `templates/ajouterU.html` + `Styles/ajouterU.css` : TopBar, layout centré avec grille prénom/nom, sélection de rôle par boutons visuels.
- `templates/modifierU.html` : même structure qu'ajouterU avec les valeurs pré-remplies.
- `templates/supprimer.html` : TopBar, layout 2 colonnes — recherche à gauche, confirmation à droite.

## [3.22.3] - 2026-04-17
> Commit : `perf(rpi): reduce sqlite contention and tune gunicorn runtime`
### Modifié
- `APP.py` : `get_db_connection()` applique désormais des PRAGMA SQLite orientés performance sur Raspberry (`journal_mode=WAL`, `synchronous=NORMAL`, `busy_timeout=5000`, `temp_store=MEMORY`) afin de réduire la contention disque et les blocages ponctuels.
- `APP.py` : optimisation des filtres temporels dans `_sync_daily_log()` et `/stats` en comparant directement `sortie_ts` (bornes ISO) au lieu d'utiliser `DATE()`/`datetime()` sur la colonne, ce qui améliore l'utilisation des index.
- `APP.py` : ajout des index `idx_sortie_logs_personne` et `idx_sortie_logs_ref_sortie` pour accélérer les statistiques par personne et les accès historiques par écran.
- `Setups Linux/lancer.sh` : profil Gunicorn ajusté pour Raspberry (`--workers 1`, `--threads 2`, `--timeout 30`, `--keep-alive 2`, `--max-requests 500`, `--max-requests-jitter 100`) afin de limiter la contention SQLite et stabiliser la latence.

## [3.22.2] - 2026-04-16
> Commit : `Readme Update`
### Modifié
- `README.md` : Mis a jours avec les informations récentes.

## [3.22.1] - 2026-04-15
> Commit : 'refactor(ecran) change the modifier button to send the user to gerer_ecrans'
### Modifié
- `Ecran.html` : Le bouton modifier envoie mainternant vers gerer_ecran.html au lieu de modifier.html.

## [3.22.0] - 2026-04-14
> Commit : `feat(gerer_ecrans): add full screen management page with search, edit, delete`
### Ajouté
- `APP.py` (`/gerer_ecrans`) : route GET+POST — recherche par référence exacte ou suffixe, affichage de toutes les infos de l'écran, suppression directe avec confirmation JS. Redirige vers `/modifier` pour l'édition.
- `Templates/gererE.html` : page complète de gestion — bouton "Ajouter un écran" en haut, formulaire de recherche, tableau d'infos (emplacement en vert), bouton "Modifier" (jaune) et "Supprimer" (rouge). Notation pointée utilisée dans `onsubmit` pour éviter les conflits de quotes avec Jinja2.
- `Styles/gererE.css` : styles de la page (tableau, boutons, lien ajouter).
### Modifié
- `Templates/index.html` : les 3 liens "Ajouter / Modifier / Supprimer un écran" remplacés par un seul "Gérer les écrans".

## [3.21.0] - 2026-04-14
> Commit : `feat(index): group screen management actions into submenu`
### Ajouté
- `APP.py` : route `GET /gerer_ecrans` (@admin_required) — sous-menu regroupant Ajouter / Modifier / Supprimer un écran.
- `Templates/gererE.html` : page du sous-menu avec 3 boutons et retour au menu.
### Modifié
- `Templates/index.html` : les 3 liens "Ajouter / Modifier / Supprimer un écran" remplacés par un seul "Gérer les écrans".

## [3.20.0] - 2026-04-14
> Commit : `feat(users): add user management page with edit and delete`
### Ajouté
- `APP.py` : 3 nouvelles routes admin — `GET /gerer_utilisateurs` (liste), `GET+POST /modifierU` (édition), `POST /supprimerU` (suppression avec protection anti-auto-suppression). Import `url_for` ajouté.
- `Templates/gererU.html` : tableau de tous les utilisateurs avec boutons Modifier et Supprimer (confirmation JS).
- `Templates/modifierU.html` : formulaire pré-rempli de modification, réutilise `ajouterU.css`.
- `Styles/gererU.css` : styles du tableau utilisateurs.
- `Templates/index.html` : lien "Ajouter un utilisateur" remplacé par "Gérer les utilisateurs" (`/gerer_utilisateurs`).
- `tests/web/test_user_management.py` : 7 nouveaux tests couvrant accès, liste, modification, doublon identifiant, suppression et protection auto-suppression.

## [3.19.0] - 2026-04-14
> Commit : `feat(stats): add date range filter`
### Ajouté
- `APP.py` (`/stats`) : paramètres GET `date_debut` et `date_fin` pour filtrer les stats par plage de dates. Les deux requêtes SQL (écrans et personnes) appliquent le filtre via `DATE(sortie_ts)`. Fonctionne aussi avec un seul des deux paramètres.
- `Templates/stats.html` : formulaire de filtrage par dates avec label de plage active et lien "Réinitialiser".
- `Styles/stats.css` : styles pour le formulaire de filtre (`.stats-filter`, `.stats-filter-reset`, `.stats-filter-label`).
- `tests/web/test_stats.py` : 3 nouveaux tests couvrant filtre avec plage complète, exclusion hors plage, et filtre `date_debut` seul.

## [3.18.5] - 2026-04-14
> Commit : `feat(prendre): show screen details after taking`
### Modifié
- `APP.py` (`/prendre`) : passe désormais `apercu` (données de l'écran) au template après chaque opération — prise réussie ou écran déjà sorti.
- `Templates/prendre.html` : affiche un bloc d'infos (emplacement en premier et en vert, puis réf., libellé, état) après la soumission du formulaire. Workflow inchangé : 1 étape.

## [3.18.4] - 2026-04-14
> Commit : `feat(ranger): add live filter input above screen dropdown`
### Ajouté
- `Templates/ranger.html` : champ texte "Filtrer…" au-dessus du `<select>` — filtre les options en temps réel (JS vanilla) et sélectionne automatiquement le premier résultat visible.

## [3.18.3] - 2026-04-14
> Commit : `feat(ecran): add confirmation dialog before taking a screen`
### Ajouté
- `Templates/ecran.html` : `onsubmit="return confirm(...)"` sur le formulaire "Prendre" du tableau — affiche la référence et le libellé de l'écran avant validation.

## [3.18.2] - 2026-04-14
> Commit : `feat(index): add ranger link on overdue screens panel`
### Ajouté
- `Templates/index.html` : bouton "Ranger" sur chaque ligne du panneau "Écrans sortis depuis +10h", redirige vers `/ranger`.

## [3.18.1] - 2026-04-14
> Commit : `feat(ecran): display who took a screen and at what time`
### Ajouté
- `APP.py` (`/ecran`) : la requête inclut désormais `sl.personne AS pris_par` et `sl.sortie_ts` via `LEFT JOIN sortie_logs` (sous-requête corrélée sur le dernier log ouvert par écran).
- `Templates/ecran.html` : nouvelle colonne "Pris par" (index 9) affichant `prénom à HH:MM` pour les écrans sortis, vide sinon. Filtre texte inclus.

## [3.18.0] - 2026-04-14
> Commit : `test(update, modifier): add missing route tests`
### Ajouté
- `tests/web/test_update.py` : 5 tests pour la route `/update` — accès non-admin (403 JSON), OS non-Linux (`will_restart: false`), Linux (`will_restart: true`, thread mocké), et vérification du champ `branch`.
- `tests/web/test_screen_management.py` : test `test_modifier_requires_admin` — vérifie la redirection vers `/` sans session.

## [3.17.9] - 2026-04-14
> Commit : `refactor(ajouterU): remove redundant SELECT before INSERT`
### Modifié
- `APP.py` (`ajouterU`) : suppression du `SELECT` manuel avant `INSERT`. La contrainte `UNIQUE` de la base suffit — on attrape directement l'`IntegrityError` et on en extrait le message, comme dans la route `ajouter`.

## [3.17.8] - 2026-04-14
> Commit : `refactor(routes): replace os.path with pathlib in send_functions and send_images`
### Modifié
- `APP.py` : `send_functions` et `send_images` utilisent désormais `BASE_DIR / 'Functions'` et `BASE_DIR / 'Images'` (pathlib) au lieu de `os.path.abspath` + `os.path.join`. Les commentaires redondants ont été supprimés.

## [3.17.7] - 2026-04-14
> Commit : `refactor(index): extract inline update JS into Functions/update.js`
### Ajouté
- `Functions/update.js` : logique du bouton "Mettre à jour" (fetch `/update`, affichage résultat, compte à rebours de redémarrage). Encapsulée dans une IIFE.
### Modifié
- `Templates/index.html` : bloc `<script>` inline remplacé par `<script src="/Functions/update.js"></script>`.

## [3.17.6] - 2026-04-14
> Commit : `refactor(templates): replace hardcoded paths with url_for()`
### Modifié
- `Templates/ajouterU.html`, `prendre.html`, `import_conflicts.html`, `modifier.html`, `ajouter.html`, `index.html`, `login.html` : tous les chemins hardcodés (`href="/..."`, `action="/..."`, `formaction="/..."`) remplacés par `url_for()`. Les chemins statiques (`/Styles/`, `/Images/`, `/Functions/`) sont conservés tels quels.

## [3.17.5] - 2026-04-14
> Commit : `refactor(db): run _ensure_log_tables once at startup instead of per-request`
### Modifié
- `APP.py` : `_ensure_log_tables()` déplacée dans un `before_request` (`_ensure_log_tables_once`) qui s'exécute au plus une fois par cycle de vie de l'application, dès que la base est disponible. Les routes exemptées (`/setup`, `/setup/init_db`, `/shutdown`, statiques) ne déclenchent pas la vérification. Les 5 appels inline dans `laver`, `prendre`, `ranger`, `stats` et `reset_stats` ont été supprimés.

## [3.17.4] - 2026-04-14
> Commit : `refactor(auth): introduce login_required and admin_required decorators`
### Ajouté
- `APP.py` : décorateurs `login_required` et `admin_required` (via `functools.wraps`). `login_required` redirige vers `/` si non connecté ; `admin_required` redirige vers `/` si non connecté, vers `/index` si non admin.
### Modifié
- `APP.py` : 14 routes mises à jour pour utiliser les décorateurs à la place du boilerplate inline (`if 'prenom' not in session` / `if 'admin' not in session`). Les 2 routes JSON (`/next_emplacement`, `/update`) conservent leur vérification inline car elles retournent un 403 JSON.
- `tests/web/test_ajouter.py`, `test_screen_management.py`, `test_user_management.py` : 3 tests mis à jour pour refléter le nouveau comportement (sans session → redirection vers `/` et non `/index`).

## [3.17.3] - 2026-04-14
> Commit : `fix: correct four bugs identified during code audit`
### Corrigé
- `APP.py` (`ajouter`) : variable `error_message` pouvait être non liée si une `IntegrityError` générée par SQLite ne correspondait pas au pattern `UNIQUE constraint failed`. Ajout d'un `else` qui affiche le message brut.
- `APP.py` (`close_db`) : la route rendait `index.html` sans les variables requises par le template (`a_laver`, `alerte_sortis`, etc.), provoquant une erreur Jinja. La route redirige désormais vers `/index`.
- `APP.py` (`ecran`) : la requête SQL n'avait pas de clause `ORDER BY`. Les écrans sont maintenant triés par emplacement `n` par défaut.
- `Templates/ranger.html` : le dropdown des écrans sortis n'affichait pas l'emplacement physique `n`. Chaque option affiche maintenant `[n] Libellé — ref_ecran`.
### Modifié
- `tests/web/test_close_db.py` : mis à jour pour valider la redirection 302 vers `/index` au lieu de l'ancien comportement 200.
- `tests/system/test_shutdown.py` : ajout d'un test documentant que `/shutdown` est intentionnellement accessible sans authentification (bouton kiosque sur la page de login).

## [3.17.2] - 2026-04-13
> Commit : `chore(linux): centralize repo URL in shared config.env`
### Ajouté
- `Setups Linux/config.env` : fichier de configuration centralisé pour les scripts Linux. Contient `REPO_URL` et `REPO_DOC_URL`. En cas de changement de propriétaire GitHub, **seul ce fichier est à modifier**.
- `CHANGER_REPO.md` : procédure complète décrivant tous les fichiers à mettre à jour en cas de changement de propriétaire ou de nom du dépôt GitHub.
### Modifié
- `Setups Linux/demarrage_release.sh`, `demarrage_branche.sh`, `installer_service_rpi.sh` : suppression de `REPO_URL` hardcodé, source `config.env` au démarrage. Le `Documentation=` du service systemd utilise désormais `${REPO_DOC_URL}`.
- `Setups Linux/Legacy/DémarrageTest.sh`, `Setup_release.sh` : idem, source `../config.env` (chemin relatif depuis Legacy).

## [3.17.1] - 2026-04-13
> Commit : `feat(index): display active branch and commit name below main container`
### Ajouté
- Affichage de la branche git active et du nom du dernier commit (message complet, sans hash) en bas du container principal sur la page d'accueil.
### Modifié
- `APP.py` : `commit` récupéré via `git log -1 --pretty=format:%s` (message seul) et passé au template.
- `Templates/index.html` : labels branche et commit déplacés à l'intérieur de `.form-container` pour apparaître sous le container et non à sa droite.

## [3.17.0] - 2026-04-13
> Commit : `feat(index): add git pull + service restart button for admins`
### Ajouté
- Route `POST /update` (admin uniquement) : exécute `git pull`, récupère la branche courante, redémarre `rpi-localwebserver` via `sudo systemctl restart` après 2s (Linux uniquement).
- Bouton « Mettre à jour » dans la section admin de `/index` : déclenche la mise à jour via fetch, affiche la branche et le résultat du pull, puis compte à rebours de 8s avant rechargement automatique de la page.

## [3.16.2] - 2026-04-13
> Commit : `feat(ajouter): auto-fill next free slot number`
### Ajouté
- Route `GET /next_emplacement` : retourne en JSON le plus petit numéro d'emplacement libre (`n`) en cherchant d'abord les trous (ex. si 133 est libre mais le max est 145, retourne `"133"`).
- Bouton « Emplacement libre » à côté du champ `n` dans `ajouter.html` : remplit automatiquement le champ via un appel fetch à `/next_emplacement`.

## [3.16.1] - 2026-04-07
> Commit : `feat(ecran): add column sorting to screen table`
### Ajouté
- `Functions/Ecran.js` : tri par colonne au clic sur l'en-tête. 1er clic → croissant (▲), 2e → décroissant (▼), 3e → retour à l'ordre d'origine. Tri numérique automatique pour les colonnes de nombres, sinon tri alphabétique (`localeCompare` fr). Compatible avec le filtrage existant.
- `Styles/ecran.css` : indicateurs `▲`/`▼` via `::after`, curseur `pointer` et survol légèrement plus clair sur les colonnes triables.

## [3.16.0] - 2026-04-07
> Commit : `feat(index): alert panel for screens out more than 10h`
### Ajouté
- Panneau `longtemps-actions` affiché à gauche (empilé sous `laver-actions`) sur `/index` quand un ou plusieurs écrans sont sortis depuis plus de 10 heures. Affiche la référence, le libellé et le nombre d'heures. Bordure orange `#FF8C00`, même structure que `laver-actions`.
- Wrapper `.panneaux-gauche` (flex colonne) pour empiler proprement les deux panneaux gauches.

## [3.15.4] - 2026-04-01
> Commit : `feat(index): show alert when more than 4 screens are out`
### Ajouté
- Panneau `sortis-alerte` affiché à droite du container principal sur `/index` quand plus de 4 écrans sont marqués comme sortis. Affiche le message "Range tes écrans Boun" avec le même style que le panneau "Écrans à laver" (bordure jaune `#feed00`).

## [3.15.3] - 2026-04-01
> Commit : `fix(import): strip spaces from ref_ecran and pcb before insert`
### Corrigé
- `_parse_import_file` : les champs `ref_ecran` et `pcb` (colonnes `INTEGER` en DB) étaient importés avec des espaces de formatage Excel (`'260 023 566'`), provoquant une erreur `datatype mismatch` silencieuse sur 104 lignes sur 149. Les espaces sont désormais retirés après parsing, avant retour des lignes.

## [3.15.2] - 2026-04-01
> Commit : `fix(import): read xlsx into BytesIO to ensure seekable stream`
### Corrigé
- `_parse_import_file` : le stream de l'upload Flask n'est pas garanti seekable ni à position 0 lors du passage à openpyxl. Le fichier est maintenant lu entièrement en mémoire via `file_storage.read()` → `BytesIO` avant d'être ouvert par openpyxl, ce qui éliminait la troncature silencieuse à ~45 lignes.

## [3.15.1] - 2026-04-01
> Commit : `fix(import): reset xlsx dimensions to bypass truncated metadata`
### Corrigé
- `_parse_import_file` : ajout de `ws.reset_dimensions()` après chargement du workbook en mode `read_only`. Sans cela, openpyxl s'arrêtait à la ligne déclarée dans la métadonnée `<dimension>` du fichier (souvent incorrecte), tronquant l'import à ~45 lignes.

## [3.15.0] - 2026-04-01
> Commit : `feat(ui): add CW and CCW rotation buttons`
### Ajouté
- `Functions/rotation.js` : script global qui injecte deux boutons flottants (bas-gauche) : `↺` anti-horaire et `↻` horaire, permettant de pivoter l'affichage par pas de 90° dans les deux sens. L'angle est persisté dans `localStorage` et réappliqué immédiatement au chargement de chaque page.
- `Styles/common.css` : classes `.rot-90`, `.rot-180`, `.rot-270` appliquées sur `<html>` avec compensation des dimensions (`100vh`/`100vw` inversés) et repositionnement pour remplir l'écran après rotation.
- `rotation.js` inclus dans les 12 templates.

## [3.14.1] - 2026-04-01
> Commit : `feat(stats): add reset stats button for admins`
### Ajouté
- Route `POST /reset_stats` : vide la table `sortie_logs` (admin uniquement) et redirige vers `/stats`.
- Bouton « Remettre les stats à zéro » en bas de `stats.html`, avec confirmation native avant exécution.

## [3.14.0] - 2026-04-01
> Commit : `feat(prendre): allow partial suffix match on screen reference`
### Ajouté
- Recherche par suffixe dans `/prendre` : l'utilisateur peut saisir uniquement les derniers caractères d'une référence écran pour la retrouver. Si plusieurs écrans correspondent, un message de désambiguïsation liste les références trouvées.

## [3.13.3] - 2026-03-31
> Commit : `fix(ui): harmonize screen location style across prendre and ranger`
### Modifié
- `Styles/common.css` : ajout de la classe `.n-value` (texte vert `#4CAF50`, sans fond) pour l'affichage de l'emplacement d'un écran.
- `Styles/prendre.css` : suppression du doublon `.n-value` désormais défini dans `common.css`.
- `Templates/ranger.html` : classe `success-message` remplacée par `n-value` sur le paragraphe d'emplacement.

## [3.13.2] - 2026-03-31
> Commit : `fix(prendre): show screen location when already taken`
### Corrigé
- `/prendre` : affiche désormais l'emplacement (`n`) de l'écran même lorsqu'il est déjà sorti, en plus du message d'erreur existant.

## [3.13.1] - 2026-03-31
> Commit : `feat(ui): add in-page virtual keyboard for kiosk touchscreen`
### Ajouté
- `Functions/vkeyboard.js` : clavier virtuel AZERTY en JavaScript pur (aucune dépendance externe, fonctionne hors-ligne). S'affiche automatiquement en bas de page au focus d'un champ texte et se cache à la perte du focus. Supporte majuscules (MAJ), backspace (`<--`), espace et validation du formulaire (`OK`). Affiche une barre de saisie au-dessus du clavier indiquant le placeholder du champ et la valeur en cours de frappe.
- `Styles/vkeyboard.css` : styles du clavier virtuel (thème sombre, touches 48px minimum pour usage tactile, barre de saisie en police monospace).
### Modifié
- `Templates/login.html`, `prendre.html`, `ajouter.html`, `ajouterU.html`, `modifier.html`, `supprimer.html`, `setup.html` : ajout des includes `vkeyboard.css` et `vkeyboard.js`.

## [3.12.0] - 2026-03-31
> Commit : `feat(linux): add kiosk installer for Raspberry Pi OS`
### Ajouté
- `Setups Linux/installer_service_rpi.sh` : script d'installation tout-en-un pour Raspberry Pi OS en mode kiosque. Configure le service systemd `rpi-localwebserver.service` (Gunicorn, démarrage automatique au boot), active l'auto-login au bureau via `raspi-config` ou lightdm, génère `Setups Linux/kiosk_browser.sh` (attend que le serveur réponde puis ouvre Firefox en plein écran, désactive l'économiseur d'écran, lance `onboard` pour le clavier virtuel sur les champs texte) et enregistre ce script dans `~/.config/autostart/` pour un lancement automatique à chaque démarrage du bureau. Compatible `firefox-esr` et `firefox`. Installe automatiquement `onboard` si absent.

## [3.10.1] - 2026-03-16
> Commit : `refactor(windows): centralize setup scripts config in config.bat`
### Ajouté
- `Setups Windows/config.bat` : nouveau fichier de configuration centralisée pour tous les scripts Windows (`PROJECT_DIR`, `REPO_URL`, `VENV_DIR`).
### Modifié
- `Setups Windows/Démarrage.bat`, `DémarrageTest.bat`, `Lancer.bat` et `Purge.bat` : les déclarations de variables en dur sont remplacées par `call "%~dp0config.bat"`. Modifier uniquement `config.bat` suffit désormais pour adapter l'installation.

## [3.10.0] - 2026-03-16
> Commit : `feat(config): add dotenv environment file support`
### Ajouté
- Support des fichiers `.env` via `python-dotenv` : `APP.py` charge automatiquement `.env` à la racine du projet au démarrage, sans écraser les variables déjà définies dans le shell.
- `.env.example` (versionné) : template documenté listant toutes les variables d'environnement disponibles (`APP_INSTANCE_DIR`, `DATABASE_PATH`, `APP_LOGS_DIR`, `APP_HOST`, `APP_PORT`, `FLASK_DEBUG`, `FLASK_SECRET_KEY`, `APP_AUTO_OPEN_BROWSER`, `APP_BROWSER_URL`, `APP_BROWSER_CMD`) avec leurs valeurs par défaut.
- `.env.development` : configuration prête à l'emploi pour le développement local (debug activé, ouverture auto du navigateur).
- `.env.production` : configuration prête à l'emploi pour le déploiement sur Raspberry Pi / serveur Linux (écoute réseau, debug désactivé).
- `.gitignore` mis à jour pour ignorer `.env` et `.env.*` tout en versionnant `.env.example`.
- `python-dotenv` ajouté à `requirements.txt`.
- `Setups Linux/demarrage_release.sh` et `demarrage_branche.sh` : ajout d'une étape `setup_env()` qui crée automatiquement `.env` depuis `.env.production` lors de la première installation, avec rappel pour définir `FLASK_SECRET_KEY`.
- `Setups Linux/lancer.sh` : avertissement affiché au démarrage si aucun fichier `.env` n'est présent.
- `Setups Windows/Démarrage.bat` et `DémarrageTest.bat` : ajout d'une étape de vérification/création du `.env` depuis `.env.production` lors du déploiement.
- `Setups Windows/Lancer.bat` : avertissement affiché si aucun fichier `.env` n'est présent.

## [3.9.0] - 2026-02-27
> Commit : `feat(setup): add new DB and shutdown buttons to setup page`
### Ajouté
- Bouton **Nouvelle BDD** (en haut à gauche) sur la page de configuration : crée une nouvelle base de données SQLite vide depuis `database/schema.sql` à l'emplacement configuré, avec un compte administrateur par défaut (`admin`), et redirige vers la page de connexion.
- Bouton **Éteindre** (en haut à droite) sur la page de configuration : déclenche l'arrêt du système via `POST /shutdown`, avec le même style rouge que le bouton éteindre de la page de connexion.
- Route `POST /setup/init_db` dans `APP.py` : crée ou réinitialise la base de données depuis `schema.sql`, exemptée du garde `_check_db_configured`.
- Constante `SCHEMA_PATH` dans `APP.py` pointant vers `database/schema.sql`.
- Tests unitaires pour la route `/setup/init_db` dans `tests/system/test_db_setup.py`.

## [3.8.3] - 2026-02-27
> Commit : `chore(windows): add run.bat shortcut at project root`
### Ajouté
- `run.bat` à la racine du projet : lance directement le serveur Waitress via le venv local (`.venv`), sans cloner ni vérifier les prérequis. Ouvre le navigateur après 3 secondes. Affiche un message d'erreur clair si le venv est absent.

## [3.8.2] - 2026-02-27
> Commit : `fix(windows): hardcode installation path in Lancer.bat`
### Corrigé
- `Setups Windows/Lancer.bat` : le chemin du projet est désormais codé en dur à `%USERPROFILE%\RPI_LocalWebServer-Release`, identique à celui utilisé par `Démarrage.bat`, pour éviter toute erreur de résolution de chemin relatif.

## [3.8.1] - 2026-02-27
> Commit : `fix(windows): resolve project path via pushd/CD in Lancer.bat`
### Modifié
- `Setups Windows/Lancer.bat` : le chemin du projet est résolu via `pushd "%~dp0.." / set PROJECT_DIR=%CD% / popd` — remonte d'un niveau depuis `Setups Windows\` pour obtenir la racine du projet. `pause` systématique en fin de script. Aucune variable système restreinte requise.

## [3.8.0] - 2026-02-27
> Commit : `feat(windows,linux): add simple launch scripts without setup or git operations`
### Ajouté
- `Setups Windows/Lancer.bat` : lance le serveur Waitress directement depuis le venv local, sans cloner ni vérifier les prérequis. Ouvre le navigateur après 3 secondes via PowerShell. Affiche un message clair si le venv est absent.
- `Setups Linux/lancer.sh` : lance le serveur Gunicorn directement depuis le venv local, sans cloner ni vérifier les prérequis. Affiche l'adresse locale et réseau. Affiche un message clair si le venv est absent.

## [3.7.1] - 2026-02-27
> Commit : `fix(windows): fix venv setup flow and delegate browser opening to PowerShell`
### Modifié
- `Setups Windows/Démarrage.bat` : correction du flux de création du venv (création et activation séparées). Installation des dépendances via `pip install -r requirements.txt` (au lieu d'une liste codée en dur). Ouverture automatique du navigateur déléguée à PowerShell avec délai de 3 secondes (`Start-Sleep -Seconds 3; Start-Process ...`), indépendamment du processus serveur.
- `requirements.txt` : suppression de `configparser` (module de la bibliothèque standard Python 3, ne nécessite pas d'installation).

## [3.7.0] - 2026-02-27
> Commit : `feat(setup): add web-based DB path configuration with config.ini persistence`
### Ajouté
- `APP.py` : `CONFIG_PATH` — chemin vers `instance/config.ini` (ignoré par Git). `_load_db_path_from_config()` — lit le chemin de la DB depuis `config.ini`. `_save_db_path_to_config()` — sauvegarde le chemin dans `config.ini`. `_check_db_configured()` — hook `before_request` qui redirige vers `/setup` si la DB est introuvable (excepté `/setup`, `/shutdown` et les fichiers statiques). Routes `GET /setup` et `POST /setup` — page web permettant de saisir et enregistrer le chemin de la base de données.
- `Templates/setup.html` : page de configuration du chemin de la base de données, réutilisant les styles `common.css` et `login.css`.
- `.gitignore` : ajout de `instance/config.ini`.
- `tests/system/test_db_setup.py` : 11 tests couvrant `database_ready()`, les routes `/setup`, le hook `before_request`, et le cycle lecture/écriture de `config.ini`.
### Modifié
- `APP.py` : initialisation de `DATABASE_PATH` — priorité variable d'environnement > `config.ini` > valeur par défaut. Suppression de la vérification `if not database_ready()` dans la route `/` (désormais gérée par `before_request`).

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
