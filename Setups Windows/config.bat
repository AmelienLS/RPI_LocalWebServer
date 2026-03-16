@echo off
:: ==============================================================================
:: config.bat — Configuration centrale des scripts Windows
::
:: Modifiez ce fichier pour adapter les chemins à votre installation.
:: Ce fichier est appelé automatiquement par les autres scripts Windows.
::
:: Variables définies :
::   PROJECT_DIR   Répertoire d'installation du projet
::   REPO_URL      URL du dépôt Git (à modifier lors d'un fork)
::   VENV_DIR      Répertoire de l'environnement virtuel Python
:: ==============================================================================

set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"
set "VENV_DIR=%PROJECT_DIR%\venv"
