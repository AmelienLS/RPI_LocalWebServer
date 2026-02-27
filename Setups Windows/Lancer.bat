@echo off
chcp 65001 >nul
setlocal

:: Remonte d'un niveau depuis "Setups Windows\" pour obtenir la racine du projet
pushd "%~dp0.."
set "PROJECT_DIR=%CD%"
popd

set "VENV_DIR=%PROJECT_DIR%\venv"

if not exist "%VENV_DIR%\Scripts\activate.bat" (
  echo [!] Environnement virtuel introuvable : %VENV_DIR%
  echo     Lancez d'abord Démarrage.bat pour installer l'application.
  pause & exit /b 1
)

cls
echo [>>>] Démarrage du serveur WSGI local...
echo     Projet : %PROJECT_DIR%
echo     URL    : http://127.0.0.1:5000
echo [!] CTRL+C pour arrêter.
echo.

call "%VENV_DIR%\Scripts\activate.bat"
pushd "%PROJECT_DIR%"
    start "" powershell -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5000'"
    python -m waitress --host=127.0.0.1 --port=5000 APP:app
    if errorlevel 1 (
        echo.
        echo [!] Le serveur s'est arrete avec une erreur.
    )
popd
call "%VENV_DIR%\Scripts\deactivate.bat"

pause
endlocal
