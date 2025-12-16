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
  echo [!] ERREUR: Python non trouvé !
  echo     https://www.python.org/downloads/
  pause & exit /b 1
)
where git >nul 2>&1
if errorlevel 1 (
  echo [!] ERREUR: Git non trouvé ! 🔧
  echo     https://git-scm.com/download/win
  pause & exit /b 1
)
echo [OK] Prérequis OK.
echo.

:: 2) Cloner ou mettre à jour le dépôt
echo [~] Mise à jour du code source...
if exist "%PROJECT_DIR%" (
  if exist "%PROJECT_DIR%\.git" (
    pushd "%PROJECT_DIR%"
      git pull
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
  git clone "%REPO_URL%" "%PROJECT_DIR%"
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
