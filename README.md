# RPI LocalWebServer

Application web développée avec Flask pour gérer des **écrans de sérigraphies** dans un atelier. Elle permet de suivre l'état des écrans (sorti / rangé / à laver), d'administrer les utilisateurs, de tracer toutes les manipulations dans des journaux CSV quotidiens, et de se déployer facilement sur une Raspberry Pi ou une machine Windows.

**Version actuelle : 3.9.0**

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Architecture du projet](#architecture-du-projet)
3. [Stack technique](#stack-technique)
4. [Base de données](#base-de-données)
5. [Variables d'environnement](#variables-denvironnement)
6. [Installation et lancement](#installation-et-lancement)
   - [Développement local](#développement-local)
   - [Déploiement Linux / Raspberry Pi](#déploiement-linux--raspberry-pi)
   - [Déploiement Windows](#déploiement-windows)
7. [Référence des routes](#référence-des-routes)
8. [Tests](#tests)
9. [Conseils de maintenance](#conseils-de-maintenance)
10. [Continuité du projet (fork)](#continuité-du-projet-fork)
11. [Contribuer](#contribuer)
12. [Licence](#licence)
13. [Historique des versions](#historique-des-versions)

---

## Fonctionnalités

| Fonctionnalité | Détail |
|---|---|
| **Gestion des écrans** | Ajout, modification, suppression, et consultation de toutes les sérigraphies |
| **Suivi d'état** | Marquer un écran comme sorti (`prendre`) ou rangé (`ranger`), avec indication du lavage |
| **Traçabilité** | Chaque emprunt/rangement est logué dans `sortie_logs` (SQLite) **et** dans un fichier CSV quotidien horodaté |
| **Authentification** | Connexion par identifiant, sessions Flask ; rôle utilisateur ou administrateur |
| **Gestion des utilisateurs** | Ajout d'utilisateurs (admin seulement) |
| **Statistiques** | Tableau de bord d'utilisation par écran et par personne (admin seulement) |
| **Import / Export** | Import CSV/XLSX d'un catalogue d'écrans avec détection de conflits, export XLSX ; export ZIP des journaux CSV |
| **Configuration web** | Page `/setup` pour choisir le chemin de la base de données et créer une nouvelle base sans toucher au code |
| **Arrêt système** | Bouton d'arrêt de la machine (Linux) ou du serveur (Windows) directement depuis l'interface |
| **Déploiement automatisé** | Scripts `bash` (Raspberry Pi / Ubuntu / Fedora) et `.bat` (Windows) pour installer et lancer le service en une commande |
| **UI tactile** | Interface optimisée pour écran tactile 12 pouces (cibles tactiles ≥ 44 px, défilement au doigt) |

---

## Architecture du projet

```
RPI_LocalWebServer/
├── APP.py                      # Application Flask principale (routes, logique, BDD)
├── wsgi.py                     # Point d'entrée WSGI pour Gunicorn
├── requirements.txt            # Dépendances Python
├── run.bat                     # Raccourci de lancement rapide (Windows, à la racine)
│
├── database/
│   └── schema.sql              # Schéma SQLite (tables users, serigraphie, sortie_logs)
│
├── scripts/
│   └── init_db.py              # CLI : crée/réinitialise la base depuis schema.sql
│
├── Templates/                  # Gabarits Jinja2 (une page = un fichier)
│   ├── login.html
│   ├── index.html
│   ├── ecran.html              # Tableau des sérigraphies avec filtres
│   ├── ajouter.html            # Formulaire ajout écran + import/export
│   ├── ajouterU.html           # Formulaire ajout utilisateur
│   ├── prendre.html            # Emprunter un écran
│   ├── ranger.html             # Ranger un écran
│   ├── modifier.html           # Modifier un écran
│   ├── supprimer.html          # Supprimer un écran
│   ├── stats.html              # Statistiques d'utilisation
│   ├── setup.html              # Configuration du chemin de la BDD
│   └── import_conflicts.html   # Résolution de conflits lors d'un import
│
├── Styles/                     # CSS dédié par page + common.css
├── Functions/
│   ├── Ecran.js                # Filtrage dynamique du tableau des écrans
│   └── ecranDrag.js            # Défilement tactile (drag horizontal)
├── Images/
│   ├── Logo.png
│   └── database.ico
│
├── Setups Linux/               # Scripts de déploiement Raspberry Pi / Ubuntu / Fedora
│   ├── demarrage_release.sh    # Setup complet + service systemd (branche Release)
│   ├── demarrage_branche.sh    # Idem avec sélection de branche
│   ├── lancer.sh               # Lancement simple (venv déjà installé)
│   ├── arreter.sh              # Arrêt propre du service
│   └── purge.sh                # Désinstallation complète
│
├── Setups Windows/             # Scripts de déploiement Windows
│   ├── Démarrage.bat           # Setup complet (clone, venv, pip, Waitress)
│   ├── Lancer.bat              # Lancement simple (venv déjà installé)
│   ├── Stop.bat                # Arrêt du serveur
│   └── Purge.bat               # Désinstallation complète
│
├── tests/                      # Suites de tests automatisés
│   ├── conftest.py             # Fixtures pytest (app, client, BDD en mémoire)
│   ├── web/                    # Tests des routes Flask
│   ├── db/                     # Tests du schéma SQLite
│   ├── scripts/                # Tests du script init_db.py
│   ├── system/                 # Tests d'intégration (logs, shutdown, setup)
│   └── js/                     # Tests JavaScript (Vitest + JSDOM)
│
└── instance/                   # Répertoire runtime — ignoré par Git
    ├── armoire.db              # Base SQLite générée localement
    ├── config.ini              # Chemin de la BDD persisté (ignoré par Git)
    └── logs/                   # Fichiers CSV quotidiens (JJ-MM-AAAA.csv)
```

> **`instance/`** n'est jamais versionné. Il est créé automatiquement au premier lancement ou lors de l'initialisation de la base.

---

## Stack technique

| Couche | Technologie |
|---|---|
| Backend | Python 3, Flask |
| Base de données | SQLite 3 (via `sqlite3` stdlib) |
| Serveur WSGI (Linux) | Gunicorn |
| Serveur WSGI (Windows) | Waitress |
| Génération / lecture Excel | openpyxl |
| Templates | Jinja2 |
| Frontend | HTML5, CSS3, JavaScript vanilla |
| Tests Python | pytest |
| Tests JavaScript | Vitest + JSDOM |

---

## Base de données

### Schéma ([database/schema.sql](database/schema.sql))

**Table `users`** — comptes de connexion

| Colonne | Type | Contrainte | Description |
|---|---|---|---|
| `id` | INTEGER | PK auto | Identifiant interne |
| `nom` | TEXT | NOT NULL | Nom de famille |
| `prenom` | TEXT | NOT NULL | Prénom |
| `identifiant` | TEXT | UNIQUE NOT NULL | Code de connexion |
| `admin` | INTEGER | — | `1` = administrateur, `0` = utilisateur |

**Table `serigraphie`** — inventaire des écrans

| Colonne | Type | Contrainte | Description |
|---|---|---|---|
| `ref_ecran` | INTEGER | PK | Référence de l'écran |
| `libelle` | TEXT | NOT NULL | Libellé descriptif |
| `pcb` | INTEGER | — | Numéro de PCB associé |
| `fab` | TEXT (2 car.) | NOT NULL | Code fabricant |
| `n_fab` | TEXT | — | Numéro fabricant (F + 6 car.) |
| `type` | TEXT | NOT NULL | Type d'écran |
| `n` | TEXT (3 car.) | UNIQUE NOT NULL | Emplacement physique (casier) |
| `sorti` | INTEGER | DEFAULT 0 | `0` = rangé, `1` = sorti |
| `lave` | INTEGER | DEFAULT 1 | `0` = à laver, `1` = propre |

**Table `sortie_logs`** — traçabilité des mouvements

| Colonne | Type | Description |
|---|---|---|
| `id` | INTEGER PK | Identifiant interne |
| `ref_ecran` | INTEGER | Référence de l'écran (FK logique) |
| `libelle` | TEXT | Libellé au moment du mouvement |
| `personne` | TEXT | Qui a pris l'écran |
| `personne_rangement` | TEXT | Qui l'a rangé |
| `sortie_ts` | TEXT | Horodatage de sortie (ISO 8601) |
| `rangement_ts` | TEXT | Horodatage de rangement |
| `lavee` | INTEGER | `0` = non lavé, `1` = lavé, NULL = en cours |

### Initialiser ou réinitialiser la base

```bash
python scripts/init_db.py --force \
  --admin-identifiant admin \
  --admin-prenom Admin \
  --admin-nom Utilisateur
```

**Options disponibles :**

| Option | Description |
|---|---|
| `--force` | Écrase un fichier `.db` existant |
| `--database /chemin/custom.db` | Emplacement personnalisé (défaut : `instance/armoire.db`) |
| `--admin-identifiant <id>` | Identifiant du compte admin créé |
| `--admin-prenom <prénom>` | Prénom de l'admin |
| `--admin-nom <nom>` | Nom de l'admin |
| `--skip-admin` | Ne crée aucun utilisateur (utile si injection manuelle) |

> Les CSV quotidiens dans `instance/logs/` sont régénérés depuis `sortie_logs`. Vous pouvez les supprimer sans perte de données : ils seront recréés à la prochaine manipulation.

---

## Variables d'environnement

Toutes les variables sont optionnelles. Elles peuvent être définies dans le shell ou dans un fichier `.env` (non versionné).

| Variable | Défaut | Description |
|---|---|---|
| `DATABASE_PATH` | `instance/armoire.db` | Chemin absolu ou relatif vers le fichier SQLite |
| `FLASK_SECRET_KEY` | Généré aléatoirement | Clé de chiffrement des sessions Flask |
| `FLASK_DEBUG` | `0` | Mode debug Flask (`1` pour activer) |
| `APP_HOST` | `127.0.0.1` | Adresse d'écoute du serveur (`0.0.0.0` pour accès réseau) |
| `APP_PORT` | `5000` | Port d'écoute |
| `APP_AUTO_OPEN_BROWSER` | `0` | Ouvre automatiquement le navigateur au démarrage (`1`) |
| `APP_BROWSER_CMD` | Navigateur par défaut | Commande personnalisée pour ouvrir le navigateur |
| `APP_LOGS_DIR` | `instance/logs` | Répertoire des CSV quotidiens (partage réseau, clé USB…) |
| `APP_INSTANCE_DIR` | `instance/` | Répertoire d'instance (config.ini, base de données) |

> La priorité pour `DATABASE_PATH` est : variable d'environnement > `instance/config.ini` > valeur par défaut.

---

## Installation et lancement

### Développement local

**Prérequis :** Python 3.8+, Git

```bash
# 1. Cloner le dépôt
git clone https://github.com/AmelienLS/RPI_LocalWebServer.git
cd RPI_LocalWebServer

# 2. Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer la base de données
python scripts/init_db.py --force --admin-identifiant admin

# 5. Lancer l'application
python APP.py
```

L'application est accessible sur [http://127.0.0.1:5000](http://127.0.0.1:5000).

Pour l'exposer sur le réseau local :
```bash
APP_HOST=0.0.0.0 python APP.py
```

#### Configuration de la base de données via l'interface web

Si aucune base n'est configurée, le serveur redirige automatiquement vers `/setup`. Cette page permet :
- de saisir le chemin vers une base existante,
- de créer une nouvelle base vide (bouton **Nouvelle BDD**),
- d'arrêter la machine (bouton **Éteindre**).

Le chemin est persisté dans `instance/config.ini` (ignoré par Git).

---

### Déploiement Linux / Raspberry Pi

**Prérequis :** Ubuntu, Fedora ou Silverblue avec accès Internet et `sudo`.

#### Installation complète (une seule commande)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/AmelienLS/RPI_LocalWebServer/Release/Setups%20Linux/demarrage_release.sh)
```

Ou après avoir copié le script sur la machine :

```bash
bash "Setups Linux/demarrage_release.sh"
```

Ce script :
1. Installe Python 3, `venv` et Git si absents (détecte Ubuntu/Fedora/Silverblue)
2. Clone la branche `Release` dans `~/RPI_LocalWebServer-Release`
3. Crée l'environnement virtuel et installe les dépendances
4. Initialise la base de données avec un compte `admin` par défaut
5. Crée et active un service **systemd** `armoire-release-<user>.service` (redémarre automatiquement, démarre au boot)
6. Lance Firefox en mode kiosque sur `http://127.0.0.1:5000` via un service systemd utilisateur

#### Commandes courantes sur Linux

```bash
# Lancer le serveur (venv déjà installé)
bash "Setups Linux/lancer.sh"

# Arrêter proprement le service
bash "Setups Linux/arreter.sh"

# Désinstaller complètement
bash "Setups Linux/purge.sh"

# Gérer le service systemd manuellement
systemctl status armoire-release-<user>.service
systemctl restart armoire-release-<user>.service
journalctl -u armoire-release-<user>.service -f
```

---

### Déploiement Windows

**Prérequis :** Python 3 et Git installés et accessibles dans le PATH.

#### Installation complète

Double-cliquer sur `Setups Windows/Démarrage.bat` ou l'exécuter depuis une invite de commandes :

```cmd
"Setups Windows\Démarrage.bat"
```

Ce script :
1. Vérifie la présence de Python et Git
2. Clone ou met à jour le dépôt dans `%USERPROFILE%\RPI_LocalWebServer-Release`
3. Crée l'environnement virtuel et installe les dépendances
4. Lance le serveur Waitress
5. Ouvre automatiquement le navigateur après 3 secondes

#### Lancement rapide (après installation)

Depuis la racine du projet :
```cmd
run.bat
```

Ou depuis le dossier `Setups Windows` :
```cmd
"Setups Windows\Lancer.bat"
```

#### Autres scripts Windows

```cmd
"Setups Windows\Stop.bat"    # Arrêter le serveur
"Setups Windows\Purge.bat"   # Désinstaller complètement
```

---

## Référence des routes

| Route | Méthode | Accès | Description |
|---|---|---|---|
| `/` | GET / POST | Public | Page de connexion |
| `/setup` | GET / POST | Public | Configuration du chemin de la BDD |
| `/setup/init_db` | POST | Public | Créer/réinitialiser la BDD depuis `schema.sql` |
| `/logout` | GET | Connecté | Déconnexion |
| `/index` | GET | Connecté | Page d'accueil avec menu d'actions |
| `/ecran` | GET | Connecté | Tableau de toutes les sérigraphies (filtres temps réel) |
| `/prendre` | GET / POST | Connecté | Marquer un écran comme sorti |
| `/ranger` | GET / POST | Connecté | Marquer un écran comme rangé |
| `/laver` | POST | Connecté | Marquer un écran comme lavé |
| `/close_db` | GET | Connecté | Fermer la session (rotation d'écran tactile) |
| `/ajouter` | GET / POST | Admin | Ajouter un écran |
| `/ajouterU` | GET / POST | Admin | Ajouter un utilisateur |
| `/modifier` | GET / POST | Admin | Modifier un écran |
| `/supprimer` | GET / POST | Admin | Supprimer un écran |
| `/stats` | GET | Admin | Statistiques d'utilisation |
| `/export_serigraphie` | GET | Admin | Télécharger le catalogue en `.xlsx` |
| `/import_serigraphie` | POST | Admin | Importer un fichier CSV/XLSX |
| `/import_serigraphie/confirm` | POST | Admin | Confirmer la résolution des conflits d'import |
| `/export_logs` | GET | Admin | Télécharger tous les journaux CSV en `.zip` |
| `/purge_logs` | POST | Admin | Exporter puis supprimer tous les journaux CSV |
| `/shutdown` | POST | Public | Arrêter le système (Linux) ou le serveur (Windows) |
| `/Functions/<fichier>` | GET | Public | Fichiers JavaScript statiques |
| `/Images/<fichier>` | GET | Public | Images statiques |

---

## Tests

Le projet dispose de trois suites de tests indépendantes.

### Tests Python (pytest)

Couvrent les routes Flask, le schéma SQLite, le script `init_db.py`, les journaux, le shutdown et la configuration de la BDD.

```bash
# Depuis la racine du projet (venv activé)
pytest

# Cibler un sous-dossier
pytest tests/web -q
pytest tests/db -q
pytest tests/system -q
pytest tests/scripts -q
```

**Fixtures disponibles dans `tests/conftest.py` :**

| Fixture | Description |
|---|---|
| `test_db` | BDD SQLite temporaire en mémoire initialisée depuis `schema.sql` |
| `app` | Application Flask configurée pour les tests |
| `client` | Client HTTP de test Flask |
| `set_user_session` | Injecte une session utilisateur ou admin |
| `add_user` | Insère un utilisateur dans la BDD de test |
| `add_serigraphie` | Insère un écran dans la BDD de test |

### Tests JavaScript (Vitest)

Couvrent la logique de filtrage du tableau ([Functions/Ecran.js](Functions/Ecran.js)).

```bash
cd tests/js
npm install
npm test
```

---

## Conseils de maintenance

### Ajouter un champ à la table `serigraphie`

1. Modifier [database/schema.sql](database/schema.sql)
2. Mettre à jour toutes les routes concernées dans [APP.py](APP.py) (INSERT, UPDATE, SELECT)
3. Mettre à jour les templates HTML correspondants ([Templates/ajouter.html](Templates/ajouter.html), [Templates/modifier.html](Templates/modifier.html), [Templates/ecran.html](Templates/ecran.html))
4. Réinitialiser la base avec `python scripts/init_db.py --force`
5. Mettre à jour les tests dans `tests/db/` et `tests/web/`

### Ajouter un utilisateur sans interface

```bash
# Via SQLite en ligne de commande
sqlite3 instance/armoire.db \
  "INSERT INTO users (nom, prenom, identifiant, admin) VALUES ('Dupont', 'Jean', 'jdupont', 0);"
```

### Lire la base de données

- **DB Browser for SQLite** (interface graphique, multiplateforme)
- **Extension VSCode** : SQLite3 Editor
- **Ligne de commande** : `sqlite3 instance/armoire.db`

### Sécurité

- La clé `FLASK_SECRET_KEY` doit être définie en variable d'environnement en production (sinon une clé aléatoire est générée à chaque démarrage, invalidant toutes les sessions).
- Les requêtes SQL utilisent des paramètres liés (`?`) pour prévenir les injections SQL.
- L'endpoint `/shutdown` est accessible sans authentification : assurez-vous que l'application n'est pas exposée sur Internet (`APP_HOST=127.0.0.1` par défaut).
- En production, utilisez Gunicorn (Linux) ou Waitress (Windows) et non le serveur de développement Flask.

### Journaux CSV

Les fichiers `JJ-MM-AAAA.csv` dans `instance/logs/` sont des **vues générées** de la table `sortie_logs`. Ils peuvent être supprimés ou archivés sans perte de données : l'application les recrée automatiquement depuis la BDD à la prochaine manipulation.

Pour changer l'emplacement des journaux (partage réseau, clé USB…) :
```bash
APP_LOGS_DIR=/mnt/partage/logs python APP.py
```

---

## Continuité du projet (fork)

Si vous reprenez ce projet sur un nouveau dépôt, modifiez les éléments suivants :

### 1. Scripts de déploiement Linux

- **`Setups Linux/demarrage_release.sh`** : modifier la variable `Documentation=` dans la section `[Unit]` du service systemd (ligne ~235) et toute référence à l'URL du dépôt.

### 2. Scripts de déploiement Windows

- **`Setups Windows/Démarrage.bat`** : modifier la ligne `set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"`
- **`Setups Windows/DémarrageTest.bat`** : idem
- Vérifier toutes les références au dossier `RPI_LocalWebServer-Release` si vous souhaitez le renommer.

### 3. Documentation

- Mettre à jour les liens dans ce fichier `README.md`
- Mettre à jour `CONTRIBUTING.md`
- Ajouter une entrée dans `CHANGELOG.md`

### 4. Recherche globale

```bash
grep -r "AmelienLS/RPI_LocalWebServer" .
```

---

## Contribuer

Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les conventions de commit, le processus de PR et les règles de versionnement.

---

## Licence

Distribué sous la licence MIT. Voir [LICENSE](LICENSE).

---

## Historique des versions

Les changements notables de chaque version sont documentés dans [CHANGELOG.md](CHANGELOG.md).
