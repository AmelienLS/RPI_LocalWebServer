@echo off
setlocal

echo [i] Tentative d'arret du serveur web local (port 5000)...
echo.

set "PID="
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    set "PID=%%a"
)

if defined PID (
    if "%PID%" neq "0" (
        echo [i] Serveur trouve avec le PID: %PID%. Arret en cours...
        taskkill /F /PID %PID%
        echo [OK] Le processus du serveur a ete termine.
    ) else (
        echo [i] Le port 5000 est utilise par le systeme (PID 0), impossible de l'arreter.
    )
) else (
    echo [i] Aucun serveur ne semble tourner sur le port 5000.
)

echo.
pause