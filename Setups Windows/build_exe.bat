@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

cls
title Création d'exécutable - RPI_LocalWebServer
echo [i] Préparation de l'exécutable Windows...
echo.

:: 1) Vérification de Python
echo [~] Vérification de Python...
python --version
if errorlevel 1 (
    echo [!] ERREUR: Python non trouvé !
    echo     https://www.python.org/downloads/
    pause & exit /b 1
)
echo [OK] Python trouvé.
echo.

:: 2) Vérification et installation de pip
echo [~] Vérification de pip...
python -m pip --version
if errorlevel 1 (
    echo [~] Installation de pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    if errorlevel 1 (
        echo [!] ERREUR: Impossible d'installer pip !
        if exist get-pip.py del get-pip.py
        pause & exit /b 1
    )
    if exist get-pip.py del get-pip.py
    echo [OK] pip installé.
) else (
    echo [OK] pip est déjà installé.
)
echo.

:: 3) Installation des dépendances
echo [~] Installation des dependances...
echo     Mise a jour de pip...
python -m pip install --upgrade pip
echo     Installation de PyInstaller...
python -m pip install pyinstaller

if exist requirements.txt (
    echo     Installation depuis requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [!] ERREUR: Echec de l'installation des dependances!
        pause & exit /b 1
    )
) else (
    echo     Installation de Flask...
    python -m pip install flask
    if errorlevel 1 (
        echo [!] ERREUR: Echec de l'installation de Flask!
        pause & exit /b 1
    )
)
echo [OK] Dependances installees.
echo.

:: 4) Configuration pour la construction
set "MAIN_FILE=APP.py"
set "DIST_DIR=dist"
set "WORK_DIR=build"

:: 5) Nettoyage des anciens builds
echo [~] Nettoyage des anciens builds...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
echo [OK] Nettoyage termine.
echo.

:: 6) Construction de l'executable
echo [^>^>^>] Construction de l'executable avec PyInstaller...
echo.

pyinstaller --noconfirm --clean --onedir ^
    --add-data "Templates;Templates" ^
    --add-data "Styles;Styles" ^
    --add-data "Functions;Functions" ^
    --add-data "Images;Images" ^
    --add-data "armoire.db;." %MAIN_FILE%

if exist "%DIST_DIR%\APP\APP.exe" (
    echo.
    echo [OK] Exécutable créé avec succès !
    echo     Chemin: %CD%\%DIST_DIR%\APP\APP.exe
) else (
    echo.
    echo [!] ERREUR: La création de l'exécutable a échoué !
)
echo.

pause
endlocal
