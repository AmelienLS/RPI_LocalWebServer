# Scripts de déploiement pour Windows

Ce dossier contient des scripts pour automatiser le déploiement de l'application et la configuration de l'environnement sur un système d'exploitation Windows.

## Prérequis

Avant de lancer les scripts, assurez-vous que les logiciels suivants sont installés sur votre machine et accessibles depuis le `PATH` système :

1.  **Python 3** : [Télécharger Python](https://www.python.org/downloads/windows/) (Assurez-vous de cocher "Add Python to PATH" lors de l'installation).
2.  **Git** : [Télécharger Git for Windows](https://git-scm.com/download/win).
3.  **Firefox** : [Télécharger Firefox](https://www.mozilla.org/firefox/new/).

Vous pouvez vérifier leur installation en ouvrant une invite de commandes (`cmd.exe`) et en tapant `python --version`, `git --version`, et `firefox --version`.

## Utilisation des scripts

Pour exécuter un script, faites un clic droit dessus et choisissez **"Exécuter en tant qu'administrateur"**.

### 1. `setup_armoire.bat`

Ce script réalise les actions suivantes :
- Clone ou met à jour le dépôt GitHub de l'application dans `%USERPROFILE%\RPI_LocalWebServer-Release`.
- Crée un environnement virtuel Python.
- Installe les dépendances Python (`Flask`, `waitress`).
- Crée une tâche planifiée (`armoire_server`) qui lance le serveur web automatiquement au démarrage de Windows.

Après exécution, le serveur sera accessible à l'adresse `http://127.0.0.1:5000`.

### 2. `setup_firefox_kiosk.bat`

Ce script configure Firefox pour qu'il se lance automatiquement en mode kiosque au démarrage de la session utilisateur, en affichant l'application locale.

Il crée un raccourci dans le dossier "Démarrage" de l'utilisateur courant.

---

**Note** : Les scripts sont conçus pour être aussi autonomes que possible, mais une connaissance de base de l'invite de commandes Windows peut être utile pour le dépannage.