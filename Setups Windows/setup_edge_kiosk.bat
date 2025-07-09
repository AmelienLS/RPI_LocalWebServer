@echo off
setlocal

echo [i] Configuration de l'ouverture automatique de Microsoft Edge au demarrage...

:: Variables
:: Le dossier "Startup" pour l'utilisateur courant
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=Edge Kiosk (Local App).lnk"
set "SHORTCUT_PATH=%STARTUP_DIR%\%SHORTCUT_NAME%"

:: Chemin vers l'executable de Microsoft Edge.
set "EDGE_PATH="
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "EDGE_PATH=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "EDGE_PATH=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"

if not defined EDGE_PATH (
    echo [!] ERREUR: Impossible de trouver msedge.exe.
    echo [i] Veuillez verifier que Microsoft Edge est bien installe.
    pause
    exit /b 1
)

echo [i] Microsoft Edge trouve a l'emplacement : %EDGE_PATH%

:: Utilisation de VBScript pour creer un raccourci, car c'est la methode native
set "VBS_SCRIPT=%TEMP%\create_shortcut.vbs"

echo [i] Creation du script VBS pour le raccourci...
(
    echo Set oWS = WScript.CreateObject("WScript.Shell"^)
    echo sLinkFile = "%SHORTCUT_PATH%"
    echo Set oLink = oWS.CreateShortcut(sLinkFile^)
    echo oLink.TargetPath = "%EDGE_PATH%"
    echo oLink.Arguments = "--kiosk http://localhost:5000"
    echo oLink.Description = "Lance Edge en mode kiosque sur l'app locale"
    echo oLink.Save
) > "%VBS_SCRIPT%"

echo [i] Creation du raccourci dans le dossier de demarrage...
cscript //nologo "%VBS_SCRIPT%"
del "%VBS_SCRIPT%"

echo.
echo [OK] Termine ! Microsoft Edge s'ouvrira automatiquement au prochain demarrage de session.
echo [i] Raccourci cree : %SHORTCUT_PATH%
echo [i] URL qui sera ouverte : http://localhost:5000
pause