@echo off
setlocal

echo [i] Tentative d'arrêt du serveur web local (port 5000)...
echo.

set "PID="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    set "PID=%%a"
)

if defined PID (
    if "%PID%" neq "0" (
        echo [i] Serveur trouvé avec le PID: %PID%. Arrêt en cours...
        taskkill /F /PID %PID%
        echo [OK] Le processus du serveur a été terminé.
    ) else (
        echo [i] Le port 5000 est utilisé par le système (PID 0), impossible de l'arrêter.
    )
) else (
    echo [i] Aucun serveur ne semble tourner sur le port 5000.
)

echo.
pause