@echo off
setlocal EnableDelayedExpansion

echo [i] Tentative d'arrêt du serveur web local (port 5000)...
echo.

REM initialisation
set "PID="

REM récupération du PID en écoute sur le port 5000
for /f "tokens=5" %%a in (
  'netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"'
) do (
  set "PID=%%a"
)

REM tests pour savoir quoi faire
if "!PID!"=="" (
    echo [i] Aucun serveur ne semble tourner sur le port 5000.
) else if "!PID!"=="0" (
    echo [i] Le port 5000 est utilisé par le système (PID 0), impossible de l'arrêter.
) else (
    echo [i] Serveur trouvé avec le PID: !PID!. Arrêt en cours...
    taskkill /F /PID !PID! >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Impossible d'arrêter le processus !PID!.
    ) else (
        echo [OK] Le processus du serveur a été terminé.
    )
)

echo.
pause