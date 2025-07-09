@echo off
setlocal

echo [i] Deploiement local SANS droits admin de l'application Flask
echo.

:: Variables
set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"
set "VENV_DIR=%PROJECT_DIR%\venv"
set "WSGI_FILE=%PROJECT_DIR%\wsgi.py"
set "RUN_SCRIPT_PATH=%PROJECT_DIR%\run_server.bat"

:: Verifier les prerequis
echo [i] Verification des prerequis (Python et Git)...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] ERREUR: Python n'est pas installe ou pas dans le PATH.
    echo [i] Veuillez l'installer depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] ERREUR: Git n'est pas installe ou pas dans le PATH.
    echo [i] Veuillez l'installer depuis https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Prerequis trouves.

:: 1. Cloner ou mettre a jour le depot
echo.
echo [1] Clonage ou mise a jour du depot Git...
if exist "%PROJECT_DIR%\.git" (
    echo [i] Le repertoire de destination existe. Mise a jour depuis Git...
    cd /d "%PROJECT_DIR%"
    git pull
) else (
    echo [i] Clonage du depot...
    git clone "%REPO_URL%" "%PROJECT_DIR%"
)
cd /d "%~dp0"

:: 2. Creer un environnement virtuel
echo.
echo [2] Creation de l'environnement virtuel...
python -m venv "%VENV_DIR%"

:: 3. Installer les dependances
echo.
echo [3] Installation de Flask et Waitress...
call "%VENV_DIR%\Scripts\activate.bat"
pip install --upgrade pip
pip install flask waitress
call "%VENV_DIR%\Scripts\deactivate.bat"

:: 4. Generer le fichier wsgi.py
echo.
echo [4] Generation du fichier wsgi.py...
(
    echo from APP import app
    echo.
    echo if __name__ == "__main__":
    echo     app.run()
) > "%WSGI_FILE%"

:: 5. Creer le script de lancement manuel
echo.
echo [5] Creation du script de lancement du serveur...
(
    echo @echo off
    echo echo [i] Demarrage du serveur web local sur http://127.0.0.1:5000
    echo echo [i] Appuyez sur CTRL+C pour arreter le serveur.
    echo call "%~dp0venv\Scripts\activate.bat"
    echo waitress-serve --host 127.0.0.1 --port 5000 wsgi:app
) > "%RUN_SCRIPT_PATH%"

echo.
echo [OK] Deploiement local termine !
echo.
echo [>] Pour lancer le serveur, executez le fichier :
echo     "%RUN_SCRIPT_PATH%"
echo.
pause