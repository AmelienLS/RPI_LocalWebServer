@echo off
setlocal

echo [i] Arret et suppression du service de l'application (tache planifiee).
echo [!] Ce script doit etre execute en tant qu'administrateur.
echo.

:: Variable
set "SERVICE_NAME=armoire_server"

:: Verifier si la tache existe
schtasks /query /tn "%SERVICE_NAME%" >nul 2>nul
if %errorlevel% neq 0 (
    echo [i] La tache planifiee "%SERVICE_NAME%" n'existe pas. Aucune action requise.
    pause
    exit /b 0
)

:: Arreter la tache si elle est en cours d'execution
echo [i] Tentative d'arret de la tache "%SERVICE_NAME%"...
schtasks /end /tn "%SERVICE_NAME%"

:: Supprimer la tache planifiee
echo [i] Suppression de la tache planifiee "%SERVICE_NAME%"...
schtasks /delete /tn "%SERVICE_NAME%" /f

echo.
echo [OK] La tache planifiee a ete supprimee avec succes.
echo [i] Le serveur ne demarrera plus automatiquement.
pause