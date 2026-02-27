@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

:: Lecture du chemin du projet depuis la configuration
set "CONFIG_FILE=%APPDATA%\RPI_LocalWebServer\config.ini"
set "PROJECT_DIR="

if not exist "%CONFIG_FILE%" (
  echo [!] Configuration introuvable : %CONFIG_FILE%
  echo     Lancez d'abord Démarrage.bat pour installer l'application.
  pause & exit /b 1
)

for /F "usebackq tokens=1,* delims==" %%A in ("%CONFIG_FILE%") do (
  if /I "%%A"=="dir" set "PROJECT_DIR=%%B"
)

if "!PROJECT_DIR!"=="" (
  echo [!] Le chemin du projet est absent de la configuration.
  echo     Lancez d'abord Démarrage.bat pour installer l'application.
  pause & exit /b 1
)

set "VENV_DIR=!PROJECT_DIR!\venv"

if not exist "!VENV_DIR!\Scripts\activate.bat" (
  echo [!] Environnement virtuel introuvable : !VENV_DIR!
  echo     Lancez d'abord Démarrage.bat pour installer l'application.
  pause & exit /b 1
)

cls
echo [>>>] Démarrage du serveur WSGI local...
echo     Projet : !PROJECT_DIR!
echo     URL    : http://127.0.0.1:5000
echo [!] CTRL+C pour arrêter.
echo.

call "!VENV_DIR!\Scripts\activate.bat"
pushd "!PROJECT_DIR!"
    start "" powershell -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5000'"
    python -m waitress --host=127.0.0.1 --port=5000 APP:app
    if errorlevel 1 (
        echo.
        echo [!] Le serveur s'est arrêté avec une erreur.
    )
popd
call "!VENV_DIR!\Scripts\deactivate.bat"

pause
endlocal
