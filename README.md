# RPI LocalWebServer

Application web développée avec Flask pour gérer des sérigraphies sur une Raspberry Pi. Elle permet de suivre l'état des écrans, d'administrer les utilisateurs et de déployer facilement le service sur un environnement embarqué.

## Fonctionnalités

- Ajout, modification, suppression et suivi des sérigraphies.
- Authentification des utilisateurs et gestion des administrateurs.
- Déploiement automatique sur Raspberry Pi (service systemd et lancement de Firefox en mode kiosque).

## Structure du Projet

Le projet est organisé comme suit :

- **Racine du projet**  
  - `APP.py` : Point d'entrée principal de l’application. Il configure Flask, définit les routes et gère la connexion à la base de données via la fonction [`get_db_connection`](app.py#L11).
  - `armoire.db` : Fichier SQLite contenant les données des sérigraphies et des utilisateurs.
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
- **Fichier [app.py](app.py)**  
  Ce fichier initialise l’application Flask :
  - **Clé secrète** : Générée dynamiquement pour sécuriser les sessions (via `secrets.token_hex(16)`).
  - **Connexion à la base de données** : La fonction `get_db_connection()` crée et retourne une connexion à la base SQLite avec une `row_factory` pour permettre l’accès par noms de colonnes.
  - **Structure optimisée** : Le code a été refactorisé pour inclure des décorateurs pour la sécurité et des fonctions utilitaires pour réduire la duplication de code.
  - **Ouverture automatique** : La page principale s’ouvre automatiquement par `webbrowser.open('http://localhost:5000/')`.

### Décorateurs et Fonctions Utilitaires
Pour améliorer la lisibilité et la maintenance, le code utilise :
- **Décorateurs `@login_required` et `@admin_required`** : Ces décorateurs sont appliqués aux routes pour s'assurer que seul un utilisateur connecté (ou un administrateur) peut y accéder. Cela centralise la logique de sécurité et évite la répétition de code.
- **Fonction `get_ecran_by_ref()`** : Une fonction utilitaire qui factorise la logique de recherche d'un écran dans la base de données, la rendant réutilisable à travers plusieurs routes.

### Routes Principales
La plupart des routes sont protégées par les décorateurs `@login_required` et/ou `@admin_required` pour sécuriser l'accès.
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
  Accessible uniquement par les administrateurs de la raspberry, cette route permet d'éteindre proprement le système (la Raspberry Pi). Elle exécute une commande système (`sudo shutdown -h now`). Un bouton rouge sur la page de connexion permet de déclencher cette action, mais elle ne fonctionnera que si une session administrateur est déjà active dans le navigateur.

### Gestion du Frontend
- **Templates HTML**  
  Chaque fichier dans le dossier [Templates](Templates/) correspond à une vue de l’application, par exemple :
  - [login.html](Templates/login.html) pour l’authentification,
  - [modifier.html](Templates/modifier.html) pour modifier une sérigraphie, etc.
  
- **Feuilles de Style**  
  Chaque fichier CSS du dossier [Styles](Styles/) correspond à une page ou un ensemble de pages et définit la présentation des éléments HTML.

- **Scripts JavaScript**  
  Les fichiers dans le dossier [Functions](Functions/) contiennent des scripts permettant, par exemple, de filtrer dynamiquement les tableaux d’affichage ([Ecran.js](Functions/Ecran.js)).

## Conseils pour la Maintenance

- **Validation et Gestion des Erreurs**  
  L’application inclut des validations pour s’assurer que les données utilisateurs respectent des contraintes précises (longueur des chaînes, format particulier, etc.). Vérifier que les conditions correspondent bien aux besoins.
  
- **Sécurité**  
  La clé secrète de l’application, générée au démarrage, sécurise la gestion des sessions. De plus, les décorateurs `@login_required` et `@admin_required` protègent les routes sensibles contre les accès non autorisés.
  
- **Modularité**  
  La séparation entre le backend (Flask et SQLite) et le frontend (HTML, CSS, JavaScript) facilite la compréhension et la maintenance du code. L'utilisation de décorateurs et de fonctions utilitaires renforce cette modularité en isolant les logiques spécifiques (sécurité, accès aux données). Attention a bien vérifier que les chemins relatifs sont bien correct pour permettre une bonne discussion entre le back et le front.

- **Base de donnée**
  la base de donnée SQLite permet de stocker toute les données. Il faut bien faire attention que les contraintes de la base de données correspondent aux contraintes donnée par le backend. Pour lire la DB, il est possible soit d'utiliser une application tierce (DB browser for SQLite par exemple) ou bien une extension Visual Studio Code (SQLite3 Editor par exemple)

## Configuration sur Raspberry Pi (Ubuntu)

Pour assurer un fonctionnement autonome sur une Raspberry Pi équipée d'Ubuntu, plusieurs scripts de configuration ont été créés pour automatiser le déploiement et le lancement de l'application.

### 1. Démarrage automatique de l'application (Service Systemd)

Le script [`setup_armoire.sh`](Setups%20Linux/setup_armoire.sh) configure l'application Flask pour qu'elle s'exécute en tant que service `systemd` au démarrage du système. Voici ses actions principales :
- **Installation des dépendances** : Installe `python3`, `venv` et `pip`.
- **Environnement virtuel** : Crée un environnement virtuel dans le dossier du projet pour isoler les dépendances Python.
- **Installation de Flask & Gunicorn** : Installe les bibliothèques nécessaires dans l'environnement virtuel. Gunicorn est utilisé comme serveur WSGI, plus robuste que le serveur de développement de Flask.
- **Création du service `armoire.service`** : Un fichier de service est créé dans `/etc/systemd/system/`. Ce service lance l'application via Gunicorn sur le port 5000.
- **Activation du service** : Le service est activé pour se lancer automatiquement à chaque démarrage (`systemctl enable armoire`).

### 2. Lancement automatique de Firefox en mode Kiosque

Pour que l'interface soit directement accessible, Firefox est configuré pour se lancer en plein écran (mode kiosque) et afficher l'application. Deux méthodes sont proposées via des scripts :

- **Méthode 1 (Autostart Desktop)** : Le script [`setup_firefox_autostart.sh`](Setups%20Linux/setup_firefox_autostart.sh) crée un fichier `.desktop` dans le dossier `~/.config/autostart`. Ce fichier exécute un script qui attend 10 secondes (pour laisser le temps au service de démarrer) puis lance Firefox en mode kiosque sur `http://localhost:5000`.

- **Méthode 2 (Service Systemd Utilisateur)** : Le script [`install_firefox_autostart_systemd.sh`](Setups%20Linux/install_firefox_autostart_systemd.sh) crée un service `systemd` au niveau de l'utilisateur. Ce service se lance après le démarrage de la session graphique et exécute la même commande pour lancer Firefox. Cette méthode est souvent plus fiable.

Grâce à cette configuration, la Raspberry Pi devient un terminal dédié à l'application : au démarrage, le serveur web se lance en arrière-plan et le navigateur s'ouvre automatiquement en plein écran sur l'interface de l'application.

## Comment Lancer le Projet
Le projet se lance automatiquement grace a la configuration de la raspberry. Dans le cas contraire, effectuer la manipultion suivante:
1. Assurez-vous que Python et Flask sont installés.
2. Placez-vous dans le dossier du projet.
3. Double cliquez sur appStartWindows ou appStartLinux selon votre environnement.
   En cas de probleme, lancez la commande :
   flask --app "app.py" run
4. Le navigateur s’ouvrira automatiquement pour afficher l’application.
5. Pour terminer le serveur, utilisez Ctrl+C dans l’invite de commande.

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

## Licence

Ce projet est distribué sous la licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d'informations.

## Historique des versions

Les changements notables de chaque version sont documentés dans le fichier [CHANGELOG.md](CHANGELOG.md).
