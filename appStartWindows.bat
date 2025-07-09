@echo off
REM Ce script démarre l'application Flask

REM Vérifier que Python est disponible
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    python3 --version >nul 2>&1
    IF %ERRORLEVEL% NEQ 0 (
        echo Python n'est pas installe ou n'est pas dans le PATH.
        pause
        exit /b
    ) ELSE (
        SET PYTHON_CMD=python3
    )
) ELSE (
    SET PYTHON_CMD=python
)

REM Activer l'environnement virtuel si present
IF EXIST venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Vérifier que app.py existe
IF NOT EXIST app.py (
    echo Le fichier app.py est introuvable.
    pause
    exit /b
)

REM Démarrage de l'application Flask
echo Démarrage de l'application Flask...
%PYTHON_CMD% app.py
IF %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'execution de l'application.
    pause
    exit /b
)

pause