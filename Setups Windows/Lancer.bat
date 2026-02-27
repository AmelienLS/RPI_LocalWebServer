@echo off
chcp 65001 >nul
setlocal

:: Variables
set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "VENV_DIR=%PROJECT_DIR%\venv"

cls
echo [>>>] Démarrage du serveur WSGI local...
echo     URL : http://127.0.0.1:5000
echo [!] CTRL+C pour arrêter.
echo.

call "%VENV_DIR%\Scripts\activate.bat"
pushd "%PROJECT_DIR%"
    start "" powershell -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5000'"
    python -m waitress --host=127.0.0.1 --port=5000 APP:app
    if errorlevel 1 (
        echo [!] Le serveur s'est arrêté avec une erreur !
        pause
    )
popd
call "%VENV_DIR%\Scripts\deactivate.bat"

endlocal
