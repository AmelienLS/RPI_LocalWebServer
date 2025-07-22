@echo off
chcp 65001 >nul
setlocal

cls
echo [i] Préparation de l'exécutable Windows...
echo.

:: 1) Vérification de Python
echo [~] Vérification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] ERREUR: Python non trouvé !
    echo     https://www.python.org/downloads/
    pause & exit /b 1
)
echo [OK] Python trouvé.
echo.

:: 2) Vérification et installation de pip
echo [~] Vérification de pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [~] Installation de pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    if errorlevel 1 (
        echo [!] ERREUR: Impossible d'installer pip !
        del get-pip.py 2>nul
        pause & exit /b 1
    )
    del get-pip.py
    echo [OK] pip installé.
) else (
    echo [OK] pip est déjà installé.
)
echo.

:: 3) Installation des dépendances
echo [~] Installation des dépendances...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pyinstaller >nul 2>&1

if exist requirements.txt (
    echo     Installation depuis requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [!] ERREUR: Échec de l'installation des dépendances !
        pause & exit /b 1
    )
) else (
    echo     Installation de Flask...
    python -m pip install flask
    if errorlevel 1 (
        echo [!] ERREUR: Échec de l'installation de Flask !
        pause & exit /b 1
    )
)
echo [OK] Dépendances installées.
echo.

:: 4) Configuration pour la construction
set "MAIN_FILE=APP.py"
set "DIST_DIR=dist"
set "WORK_DIR=build"

:: 5) Nettoyage des anciens builds
echo [~] Nettoyage des anciens builds...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
echo [OK] Nettoyage terminé.
echo.

:: 6) Construction de l'exécutable
echo [>>>] Construction de l'exécutable avec PyInstaller...
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
