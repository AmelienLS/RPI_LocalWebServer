@echo off
echo ========================================
echo Preparation de l'environnement pour la construction de l'executable
echo ========================================

REM Verification de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Verification et installation de pip si necessaire
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installation de pip...
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    del get-pip.py
)

REM Installation de PyInstaller si necessaire
echo Verification et installation des dependances...
python -m pip install --upgrade pip
python -m pip install pyinstaller

REM Installation des dependances du projet si un fichier requirements.txt existe
if exist requirements.txt (
    echo Installation des dependances du projet...
    python -m pip install -r requirements.txt
) else (
    echo Aucun fichier requirements.txt trouve.
    echo Installation des dependances courantes pour un serveur web...
    python -m pip install flask
)

REM Configuration pour la construction
set "MAIN_FILE=APP.py"
set "DIST_DIR=dist"
set "WORK_DIR=build"

echo.
echo ========================================
echo Construction de l'executable avec PyInstaller
echo ========================================

REM Nettoyage des anciens builds si existants
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
if exist %WORK_DIR% rmdir /s /q %WORK_DIR%

pyinstaller --noconfirm --clean --onedir ^
    --add-data "Templates;Templates" ^
    --add-data "Styles;Styles" ^
    --add-data "Functions;Functions" ^
    --add-data "Images;Images" ^
    --add-data "armoire.db;." %MAIN_FILE%

if exist %DIST_DIR%\APP\APP.exe (
    echo.
    echo ========================================
    echo Succes! Executable cree dans %DIST_DIR%\APP\APP.exe
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Erreur lors de la creation de l'executable.
    echo ========================================
)

pause
