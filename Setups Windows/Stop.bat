@echo off
setlocal

echo [i] Arrêt du serveur local (waitress)...
for /f "tokens=2 delims=," %%A in ('tasklist /fi "imagename eq waitress-serve.exe" /fo csv /nh') do (
    echo [i] Terminaison du PID %%~A...
    taskkill /F /PID %%~A >nul
    echo [OK] Serveur arrêté.
    goto :EOF
)
echo [i] Aucun processus waitress-serve.exe trouvé.
:EOF