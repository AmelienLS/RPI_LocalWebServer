# RPI LocalWebServer

Application web développée avec Flask pour gérer des sérigraphies sur une Raspberry Pi ou une inctance windows classique. Elle permet de suivre l'état des écrans, d'administrer les utilisateurs et de déployer facilement le service sur un environnement embarqué.

## Continuité du projet

La personne qui récupérera le projet pourra fork ce repo. Dans ce cas il faudra modifier les éléments suivants pour refléter le nouvel emplacement du dépôt :

### Fichiers à modifier lors d'un changement d'emplacement du dépôt

1. **Documentation (README.md)**
   - Mettre à jour tous les liens vers les fichiers du projet (par exemple : `[APP.py](APP.py)`, `[ecran.html](Templates/ecran.html)`, etc.)
   - Vérifier que les références au dépôt GitHub dans les liens correspondent au nouveau propriétaire/organisation

2. **Scripts de déploiement Linux**
   - **`Setups Linux/Setup_release.sh`** : Modifier la variable `Documentation=` dans la section `[Unit]` du service systemd (ligne ~235) pour pointer vers la nouvelle URL du dépôt
   - Vérifier les commentaires et messages d'erreur qui pourraient référencer l'ancien dépôt

3. **Scripts de déploiement Windows** 
   - **`Setups Windows/Démarrage.bat`** : Modifier la ligne 7 `set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"`
   - **`Setups Windows/DémarrageTest.bat`** : Modifier la ligne 7 `set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"`
   - **`Setups Windows/Setup_armoire.bat`** : Modifier la ligne 8 `set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"`
   - Également vérifier toutes les références au nom du dossier `RPI_LocalWebServer-Release` si vous souhaitez le renommer

4. **Configuration du projet**
   - **`CONTRIBUTING.md`** : Mettre à jour les instructions de contribution et les liens vers le dépôt
   - **`CHANGELOG.md`** : Ajouter une entrée mentionnant le changement d'emplacement du dépôt
   - Vérifier les éventuelles configurations dans `package.json`, `setup.py` ou autres fichiers de métadonnées

5. **Code source**
   - Rechercher dans tous les fichiers Python (`.py`) et JavaScript (`.js`) les éventuelles références codées en dur à l'ancien dépôt
   - Vérifier les commentaires de copyright ou de licence qui mentionnent le propriétaire original

### Recommandations
- Utiliser une recherche globale (par exemple `grep -r "AmelienLS/RPI_LocalWebServer"`) pour identifier toutes les références à l'ancien dépôt
- Tester le déploiement après modification pour s'assurer que tous les liens et références fonctionnent correctement
- Mettre à jour la documentation pour mentionner le fork et créditer le projet original

## Fonctionnalités

- Ajout, modification, suppression et suivi des sérigraphies.
- Authentification des utilisateurs et gestion des administrateurs.
- Déploiement automatique sur Raspberry Pi (service systemd et lancement de Firefox en mode kiosque).

## Structure du Projet

Le projet est organisé comme suit :

- **Racine du projet**  
  - `APP.py` : Point d'entrée principal de l’application. Il configure Flask, définit les routes et gère la connexion à la base de données via la fonction [`get_db_connection`](APP.py#L76).
  - `instance/` : Répertoire ignoré par Git qui héberge la base SQLite générée localement (`instance/armoire.db`).
  - `scripts/init_db.py` : Script CLI qui crée/réinitialise la base en appliquant le schéma situé dans [`database/schema.sql`](database/schema.sql).
  - `README.md` : Documentation principale du projet.
  
- **Dossier Templates/**  
  Contient tous les fichiers HTML utilisés pour l’affichage des pages. Chaque page utilise un fichier CSS dédié (situé dans le dossier Styles) et certains liens spécifiques dans les balises `<link>` permettent d’inclure une icône pour l’onglet du navigateur ([Logo.png](Images/Logo.png)).
  - Exemple : [ecran.html](Templates/ecran.html) affiche le tableau des sérigraphies.
  
- **Dossier Styles/**  
  Contient les fichiers CSS pour le style de chaque page.  
  - Exemple : [ecran.css](Styles/ecran.css) assure la mise en forme du tableau présenté dans [ecran.html](Templates/ecran.html).
  
- **Dossier Functions/**  
  Contient des fichiers JavaScript pour gérer des interactions côté client (filtrage de tableau, etc.).
  - Exemple : [Ecran.js](Functions/Ecran.js) définit la logique de filtrage pour le tableau dans [ecran.html](Templates/ecran.html).

- **Dossier Images/**  
  Contient les fichiers image utilisés dans le projet, par exemple pour l’icône de l’onglet (`Logo.png` ou `database.ico`).

## Explications détaillées du Code

### Configuration et Lancement
- **Fichier [APP.py](APP.py)**  
  Ce fichier initialise l’application Flask :
  - **Clé secrète** : Chargée depuis la variable d'environnement `FLASK_SECRET_KEY`. À défaut, une valeur aléatoire sécurise les sessions pour l'exécution courante.
  - **Connexion à la base de données** : La fonction `get_db_connection()` ouvre le fichier `instance/armoire.db`. Ce fichier est généré via `scripts/init_db.py` et n'est jamais versionné.
  - **Paramètres runtime** : Les variables `APP_HOST`, `APP_PORT`, `APP_AUTO_OPEN_BROWSER` ou `APP_BROWSER_CMD` permettent d'adapter l'exécution sans modifier le code (serveur accessible sur le réseau, ouverture automatique du navigateur, etc.).

### Gestion des accès et fonctions utilitaires
- Les routes sensibles vérifient systématiquement la présence de `session['prenom']` et le flag `session['admin']` pour limiter l'accès aux utilisateurs connectés ou aux administrateurs.
- La fonction `get_db_connection()` centralise l'ouverture de la base et garantit que les résultats peuvent être parcourus par nom de colonne (`sqlite3.Row`).

### Routes Principales
Chaque route sensible commence par vérifier les informations présentes dans la session Flask et redirige vers `/` en cas d'accès non autorisé.
- **Route `/` (login)**  
  Gère l’authentification en vérifiant l’identifiant dans la table `users` de la base de données.
  
- **Route `/index`**  
  Affiche la page d’accueil une fois l’utilisateur authentifié.  
  Selon son statut (admin ou non), différentes actions (ajout, modification, suppression, etc.) sont proposées.

- **Route `/ajouter`**  
  Permet d’ajouter une nouvelle sérigraphie en collectant divers paramètres (référence, libellé, PCB, fabricant, etc.) et en effectuant des validations sur le format des données.

- **Route `/modifier`**  
  Permet de rechercher une sérigraphie par sa référence et de mettre à jour ses informations.  
  Vérifie également que la nouvelle référence n’existe pas déjà en cas de modification.

- **Route `/supprimer`**  
  Permet de vérifier l’existence d’une sérigraphie et ensuite de la supprimer de la base.

- **Route `/prendre` et `/ranger`**  
  Ces routes gèrent le changement de statut d’une sérigraphie (prise ou rangée).  
  Le statut `sorti` et une indication relative au lavage (via `lave`) sont mis à jour dans la base.

- **Route `/shutdown`**  
  Ferme proprement le service Gunicorn (Windows) ou exécute `sudo shutdown -h now` (Linux). Cette action doit être restreinte au navigateur de la Raspberry via les mécanismes d'authentification décrits plus haut.

### Gestion du Frontend
- **Templates HTML**  
  Chaque fichier dans le dossier [Templates](Templates/) correspond à une vue de l’application, par exemple :
  - [login.html](Templates/login.html) pour l’authentification,
  - [modifier.html](Templates/modifier.html) pour modifier une sérigraphie, etc.
  
- **Feuilles de Style**  
  Chaque fichier CSS du dossier [Styles](Styles/) correspond à une page ou un ensemble de pages et définit la présentation des éléments HTML.

- **Scripts JavaScript**  
  Les fichiers dans le dossier [Functions](Functions/) contiennent des scripts permettant, par exemple, de filtrer dynamiquement les tableaux d’affichage ([Ecran.js](Functions/Ecran.js)).

## Initialiser la base de données

Le dépôt ne contient plus de fichier `.db`. Chaque environnement doit générer sa base à partir du schéma partagé :

```bash
python -m venv .venv
source .venv/bin/activate            # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py --force \
  --admin-identifiant admin \
  --admin-prenom Admin \
  --admin-nom Utilisateur
```

Options utiles :

- `--database /chemin/custom.db` : change l’emplacement du fichier SQLite (par défaut `instance/armoire.db`).
- `--skip-admin` : n’ajoute aucun utilisateur. À utiliser si vous souhaitez injecter vos propres données avec un autre outil.
- `--force` : remplace un fichier existant (utile lors d’un reset complet).

Le script peut être relancé à tout moment pour repartir d’une base propre.

## Conseils pour la Maintenance

- **Validation et Gestion des Erreurs**  
  L’application inclut des validations pour s’assurer que les données utilisateurs respectent des contraintes précises (longueur des chaînes, format particulier, etc.). Vérifier que les conditions correspondent bien aux besoins.
  
- **Sécurité**  
  La clé secrète de l’application, générée au démarrage ou fournie via `FLASK_SECRET_KEY`, sécurise la gestion des sessions. Les routes vérifient explicitement la présence d'un utilisateur connecté et de son statut admin avant de poursuivre.
  
- **Modularité**  
  La séparation entre le backend (Flask et SQLite) et le frontend (HTML, CSS, JavaScript) facilite la compréhension et la maintenance du code. Les helpers centrés sur l'accès à la base et la gestion de session évitent la duplication et clarifient les responsabilités.

- **Base de donnée**
  la base de donnée SQLite permet de stocker toute les données. Il faut bien faire attention que les contraintes de la base de données correspondent aux contraintes donnée par le backend. Pour lire la DB, il est possible soit d'utiliser une application tierce (DB browser for SQLite par exemple) ou bien une extension Visual Studio Code (SQLite3 Editor par exemple)

## Configuration sur Raspberry Pi (Ubuntu)

Pour assurer un fonctionnement autonome sur une Raspberry Pi équipée d'Ubuntu, plusieurs scripts de configuration ont été créés pour automatiser le déploiement et le lancement de l'application.

### 1. Démarrage automatique de l'application (Service Systemd)

Le script [`Setup_release.sh`](Setups%20Linux/Setup_release.sh) prépare une instance autonome dans `~/RPI_LocalWebServer-release` :
- **Installation des dépendances** : Installe `python3`, `venv` et `pip`.
- **Environnement virtuel** : Crée un environnement virtuel dans le dossier de release pour isoler les dépendances Python, puis installe `Flask`, `gunicorn`, etc. via `requirements.txt`.
- **Base de données** : Exécute `scripts/init_db.py --force --admin-identifiant <id>` pour générer une base propre dans `instance/armoire.db`. Aucun fichier utilisateur n'est copié.
- **Création du service `armoire-release-<user>.service`** : Le service `systemd` lance l'application via Gunicorn sur le port 5000 (IPv4 et IPv6) et redémarre automatiquement en cas de crash.
- **Activation du service** : Le service est activé pour se lancer automatiquement à chaque démarrage (`systemctl enable armoire`).

### 2. Lancement automatique de Firefox en mode Kiosque

Le script [`Firefox_autostart.sh`](Setups%20Linux/Firefox_autostart.sh) crée un service `systemd --user` qui attend le démarrage du service web, puis lance Firefox en mode kiosque sur `http://127.0.0.1:5000`. Le script accepte désormais des variables d'environnement (`TARGET_USER`, `APP_SERVICE_NAME`, `FIREFOX_ARGS`, etc.) pour l'adapter facilement à n'importe quel compte sans éditer le fichier.

Grâce à cette configuration, la Raspberry Pi devient un terminal dédié à l'application : au démarrage, le serveur web se lance en arrière-plan, puis le navigateur s'ouvre automatiquement en plein écran sur l'interface.

## Comment Lancer le Projet (usage générique)

1. **Installer les dépendances**
   ```bash
   python -m venv .venv
   source .venv/bin/activate            # Windows : .venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. **Initialiser la base**
   ```bash
   python scripts/init_db.py --force --admin-identifiant admin
   ```
   Vous pouvez passer vos propres noms/prénoms ou l’option `--skip-admin`.
3. **Démarrer l’application**
   ```bash
   export APP_AUTO_OPEN_BROWSER=1        # Optionnel
   python APP.py                         # ou: flask --app APP run
   ```
   Les variables `APP_HOST` et `APP_PORT` permettent d’exposer l’application sur une IP différente (`APP_HOST=0.0.0.0` pour accepter les connexions réseau).
4. **Arrêter le serveur**  
   Appuyez sur `Ctrl+C` dans le terminal ou arrêtez le service systemd / la tâche planifiée suivant votre environnement.

## Création d'un exécutable Windows
Pour faciliter le déploiement sur un nouvel ordinateur, un script `build_exe.bat`
est fourni dans le dossier `Setups Windows`. Il utilise **PyInstaller** pour
générer un programme autonome contenant l'application et toutes ses ressources.

### Étapes pour générer l'exécutable
1. Installer Python sur la machine cible et s'assurer que la commande `python`
   est accessible.
2. Installer PyInstaller :
   ```cmd
   pip install pyinstaller
   ```
3. Depuis une invite de commandes, exécuter le script :
   ```cmd
   Setups Windows\build_exe.bat
   ```
4. L'exécutable sera créé dans le dossier `dist\APP\APP.exe`. Copiez ce
   dossier sur la machine souhaitée puis lancez `APP.exe` pour démarrer le
   serveur.

## Contribuer

Les contributions sont les bienvenues ! Merci de consulter le fichier [CONTRIBUTING.md](CONTRIBUTING.md) pour connaître les bonnes pratiques et le processus de soumission.

## Tests

Une suite de tests peut être exécutée avec [pytest](https://docs.pytest.org/) :

```bash
pytest
```

Si aucune vérification automatisée n’est définie, la commande s’exécutera tout de même pour confirmer qu’aucun test existant
n’échoue.

## Licence

Ce projet est distribué sous la licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

## Historique des versions

Les changements notables de chaque version sont documentés dans le fichier [CHANGELOG.md](CHANGELOG.md).
