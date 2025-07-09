@echo off
setlocal

:: Variables
set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"
set "VENV_DIR=%PROJECT_DIR%\venv"
set "WSGI_FILE=%PROJECT_DIR%\wsgi.py"

:: Lancement
cls
echo [i] Lancement et deploiement de l'application locale...
echo.

:: Verifier prerequis (Python et Git)
echo [~] Verification des prerequis...

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] ERREUR: Python non trouve !
    echo [i] Telecharge-le ici : https://www.python.org/downloads/
    pause
    exit /b 1
)

where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] ERREUR: Git non trouve !
    echo [i] Telecharge-le ici : https://git-scm.com/download/win
    pause
    exit /b 1
)
echo [OK] Prerequis OK.
echo.

:: 1. Cloner ou mettre a jour le depot
echo [~] Mise a jour du code source...

if exist "%PROJECT_DIR%\.git" (
    pushd "%PROJECT_DIR%"
    git pull
    if %errorlevel% neq 0 (
        echo [!] Erreur pendant git pull !
        popd
        pause
        exit /b 1
    )
    popd
) else (
    git clone "%REPO_URL%" "%PROJECT_DIR%"
    if %errorlevel% neq 0 (
        echo [!] Erreur pendant git clone !
        pause
        exit /b 1
    )
)
echo [OK] Code source pret.
echo.

:: 2. Environnement virtuel et dependances
echo [~] Verification de l'environnement...

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [i] Creation environnement virtuel...
    python -m venv "%VENV_DIR%"

    echo [i] Installation des dependances...
    call "%VENV_DIR%\Scripts\activate.bat"
    pip install --upgrade pip
    pip install flask waitress
    call "%VENV_DIR%\Scripts\deactivate.bat"
)
echo [OK] Environnement OK.
echo.

:: 3. Generer fichier wsgi.py
(
    echo from APP import app
    echo.
    echo if __name__ == "__main__":
    echo     app.run()
) > "%WSGI_FILE%"

:: 4. Demarrage du serveur
echo [>>>] DEMARRAGE DU SERVEUR <<<
echo.
echo     URL: http://127.0.0.1:5000
echo.
echo [!] Appuie sur CTRL+C pour arreter le serveur.
echo.

call "%VENV_DIR%\Scripts\activate.bat"
waitress-serve --host 127.0.0.1 --port 5000 wsgi:app

:: Si le serveur se ferme anormalement
if %errorlevel% neq 0 (
    echo [!] Erreur lors du demarrage du serveur !
    pause
)

endlocal
