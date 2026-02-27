@echo off
setlocal

:: ##################################################################
:: #                                                                #
:: #    ATTENTION : SCRIPT DE SUPPRESSION DEFINITIVE                #
:: #                                                                #
:: # Ce script va :                                                 #
:: # 1. Arreter et supprimer le service/tache planifiee du serveur. #
:: # 2. Supprimer le raccourci de demarrage du navigateur.          #
:: # 3. Supprimer TOUT le dossier du projet, y compris le code      #
:: #    source et l'environnement virtuel.                          #
:: #                                                                #
:: #    CETTE ACTION EST IRREVERSIBLE.                              #
:: #                                                                #
:: ##################################################################

echo.
echo [!] Ce script doit etre execute en tant qu'administrateur pour tout nettoyer.
echo.
set /p "CONFIRM=Etes-vous sur de vouloir tout supprimer ? (o/n): "
if /i not "%CONFIRM%"=="o" (
    echo [i] Annulation. Aucune modification n'a ete effectuee.
    pause
    exit /b 1
)

echo.
echo [i] Suppression en cours...

:: Variables
set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "SERVICE_NAME=armoire_server"
set "EDGE_SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Edge Kiosk (Local App).lnk"
set "APPDATA_CONFIG=%APPDATA%\RPI_LocalWebServer"

:: 1. Arreter et supprimer la tache planifiee (necessite des droits admin)
echo.
echo [1] Suppression de la tache planifiee...
net session >nul 2>&1
if %errorLevel% == 0 (
    schtasks /query /tn "%SERVICE_NAME%" >nul 2>nul
    if %errorlevel% equ 0 (
        echo [i] Arret de la tache '%SERVICE_NAME%'...
        schtasks /end /tn "%SERVICE_NAME%" >nul 2>nul
        echo [i] Suppression de la tache '%SERVICE_NAME%'...
        schtasks /delete /tn "%SERVICE_NAME%" /f >nul
        echo [OK] Tache supprimee.
    ) else (
        echo [i] Tache planifiee non trouvee.
    )
) else (
    echo [!] Pas de droits admin. Impossible de verifier/supprimer la tache planifiee.
)

:: 2. Supprimer le raccourci de demarrage du navigateur
echo.
echo [2] Suppression du raccourci de demarrage...
if exist "%EDGE_SHORTCUT_PATH%" (
    del "%EDGE_SHORTCUT_PATH%"
    echo [OK] Raccourci de demarrage pour Edge supprime.
) else (
    echo [i] Raccourci de demarrage non trouve.
)

:: 3. Supprimer le dossier du projet
echo.
echo [3] Suppression du dossier du projet...
if exist "%PROJECT_DIR%" (
    echo [i] Suppression de %PROJECT_DIR%...
    rmdir /s /q "%PROJECT_DIR%"
    echo [OK] Dossier du projet supprime.
) else (
    echo [i] Dossier du projet non trouve.
)

:: 4. Supprimer la configuration AppData (Lancer.bat)
echo.
echo [4] Suppression de la configuration AppData...
if exist "%APPDATA_CONFIG%" (
    rmdir /s /q "%APPDATA_CONFIG%"
    echo [OK] Configuration AppData supprimee.
) else (
    echo [i] Configuration AppData non trouvee.
)

echo.
echo [OK] Nettoyage termine.
pause