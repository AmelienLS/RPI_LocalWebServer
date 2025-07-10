@echo off
REM Ce script démarre l'application Flask

REM Vérifier que Python est disponible
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    pause
    exit /b
)

REM Démarrage de l'application Flask
echo Démarrage de l'application Flask...
python app.py

pause