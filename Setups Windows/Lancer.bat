@echo off
chcp 65001 >nul
setlocal

set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "VENV_DIR=%PROJECT_DIR%\venv"

cls
echo [i] Lancement de l'application...
echo.

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [!] Environnement virtuel introuvable : %VENV_DIR%
    echo     Lancez d'abord "Setups Windows\Démarrage.bat" pour installer l'application.
    pause & exit /b 1
)

if not exist "%PROJECT_DIR%\.env" (
    echo [!] Aucun fichier .env ^— configuration par defaut utilisee.
    echo     Copiez .env.production pour personnaliser :
    echo     copy "%PROJECT_DIR%\.env.production" "%PROJECT_DIR%\.env"
    echo.
)

call "%VENV_DIR%\Scripts\activate.bat"

echo [^>^>^>] Démarrage du serveur...
echo     URL : http://127.0.0.1:5000
echo [!] CTRL+C pour arrêter.
echo.

start "" powershell -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5000'"
pushd "%PROJECT_DIR%"
    python -m waitress --host=127.0.0.1 --port=5000 APP:app
    if errorlevel 1 (
        echo [!] Le serveur s'est arrête avec une erreur !
        pause
    )
popd

call "%VENV_DIR%\Scripts\deactivate.bat"
endlocal
