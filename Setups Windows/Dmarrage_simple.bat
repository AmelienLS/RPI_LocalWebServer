REM filepath: vscode-vfs://github/AmelienLS/RPI_LocalWebServer/Setups%20Windows/Dmarrage_simple.bat
@echo off
setlocal

echo [i] Lancement et deploiement de l'application locale...
echo.

:: Variables
set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"
set "VENV_DIR=%PROJECT_DIR%\venv"
set "WSGI_FILE=%PROJECT_DIR%\wsgi.py"

:: Verifier les prerequis (Python et Git)
echo [~] Verification des prerequis...
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
echo.

:: 1. Cloner ou mettre a jour le depot
echo [~] Mise a jour du code source depuis GitHub...
if exist "%PROJECT_DIR%\.git" (
    pushd "%PROJECT_DIR%"
    git pull
    popd
) else (
    git clone "%REPO_URL%" "%PROJECT_DIR%"
)
echo [OK] Code source a jour.
echo.

:: 2. Creer l'environnement virtuel et installer les dependances si necessaire
echo [~] Verification de l'environnement de l'application...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [i] Creation de l'environnement virtuel (premiere fois)...
    python -m venv "%VENV_DIR%"
    
    echo [i] Installation des dependances (Flask, Waitress)...
    call "%VENV_DIR%\Scripts\activate.bat"
    pip install --upgrade pip >nul
    pip install flask waitress >nul
    call "%VENV_DIR%\Scripts\deactivate.bat"
)
echo [OK] Environnement pret.
echo.

:: 3. Generer le fichier wsgi.py pour le serveur
(
    echo from APP import app
    echo.
    echo if __name__ == "__main__":
    echo     app.run()
) > "%WSGI_FILE%"

:: 4. Demarrer le serveur web
echo [>>>] DEMARRAGE DU SERVEUR <<<
echo.
echo     URL: http://127.0.0.1:5000
echo.
echo [!] Appuyez sur CTRL+C dans cette fenetre pour arreter le serveur.
echo.

call "%VENV_DIR%\Scripts\activate.bat"
waitress-serve --host 127.0.0.1 --port 5000 wsgi:app

endlocal