@echo off
chcp 65001 >nul
setlocal

:: Variables
set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"
set "VENV_DIR=%PROJECT_DIR%\venv"

cls
echo [i] Déploiement de l'application locale...
echo.

:: 1) Vérification des prérequis
echo [~] Vérification de Python et Git...
where python >nul 2>&1
if errorlevel 1 (
  echo [!] Python non trouvé ! Installation automatique...
  where winget >nul 2>&1
  if errorlevel 1 (
    echo [!] ERREUR: winget non disponible !
    echo     Installez manuellement Python : https://www.python.org/downloads/
    pause & exit /b 1
  )
  winget install --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo [!] Échec de l'installation de Python !
    pause & exit /b 1
  )
  echo [OK] Python installé.
)
where git >nul 2>&1
if errorlevel 1 (
  echo [!] Git non trouvé ! Installation automatique...
  where winget >nul 2>&1
  if errorlevel 1 (
    echo [!] ERREUR: winget non disponible !
    echo     Installez manuellement Git : https://git-scm.com/download/win
    pause & exit /b 1
  )
  winget install --id Git.Git --silent --accept-package-agreements --accept-source-agreements
  if errorlevel 1 (
    echo [!] Échec de l'installation de Git !
    pause & exit /b 1
  )
  echo [OK] Git installé.
  echo [i] Redémarrage du script requis pour actualiser le PATH...
  pause
  "%~f0"
  exit /b 0
)
echo [OK] Prérequis OK.
echo.

:: Affichage des branches disponibles
echo [i] Récupération des branches disponibles...
echo.
echo Branches disponibles:
git ls-remote --heads "%REPO_URL%" > "%TEMP%\git_branches.txt"
for /F "tokens=*" %%a in ('type "%TEMP%\git_branches.txt" ^| findstr "refs/heads/"') do (
  for /F "tokens=3 delims=/" %%b in ("%%a") do (
    echo - %%b
  )
)
del "%TEMP%\git_branches.txt" >nul 2>&1
echo.

:: Demande de la branche à utiliser
set /p BRANCH="[?] Quelle branche souhaitez-vous utiliser ? [main] : "
if "%BRANCH%"=="" set BRANCH=main
echo [i] Branche sélectionnée : %BRANCH%
echo.

:: 2) Cloner ou mettre à jour le dépôt
echo [~] Mise à jour du code source...
if exist "%PROJECT_DIR%" (
  if exist "%PROJECT_DIR%\.git" (
    pushd "%PROJECT_DIR%"
      git fetch >nul 2>&1
      git checkout %BRANCH% >nul 2>&1
      if errorlevel 1 (
        echo [!] Impossible de basculer sur la branche %BRANCH% !
        popd & pause & exit /b 1
      )
      git pull >nul 2>&1
      if errorlevel 1 (
        echo [!] git pull a échoué !
        popd & pause & exit /b 1
      )
    popd
  ) else (
    echo [!] "%PROJECT_DIR%" existe mais n'est PAS un dépôt Git valide !
    pause & exit /b 1
  )
) else (
  git clone -b %BRANCH% "%REPO_URL%" "%PROJECT_DIR%" >nul 2>&1
  if errorlevel 1 (
    echo [!] git clone a échoué !
    pause & exit /b 1
  )
)
echo [OK] Code source prêt.
echo.

:: 3) Création du venv + dépendances
echo [~] Préparation de l'environnement virtuel...
if not exist "%VENV_DIR%\Scripts\activate.bat" (
  echo     Création du venv...
  python -m venv "%VENV_DIR%"
  if errorlevel 1 (
    echo [!] Impossible de créer le venv !
    pause & exit /b 1
  )
  call "%VENV_DIR%\Scripts\activate.bat"
    %USERPROFILE%\RPI_LocalWebServer-Release\vend\Scripts\python.exe -m pip install 
    pip install flask waitress
    if errorlevel 1 (
      echo [!] Échec de l'installation des dépendances !
      call "%VENV_DIR%\Scripts\deactivate.bat"
      pause & exit /b 1
    )
  call "%VENV_DIR%\Scripts\deactivate.bat"
)
echo [OK] Environnement virtuel prêt.
echo.

:: 4) Lancement du serveur
echo [^>^>^>] Démarrage du serveur WSGI local...
echo     URL : http://127.0.0.1:5000
echo [!] CTRL+C pour arrêter.
for /F "delims=" %%A in ('echo prompt $E ^| cmd') do set "ESC=%%A"
echo %ESC%]8;;file:///%USERPROFILE%/RPI_LocalWebServer-Release%ESC%\Open Project Folder%ESC%]8;;%ESC%\
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
