@echo off
chcp 65001 >nul
setlocal

:: Variables
set "PROJECT_DIR=%USERPROFILE%\RPI_LocalWebServer-Release"
set "REPO_URL=https://github.com/AmelienLS/RPI_LocalWebServer.git"
set "MAIN_FILE=APP.py"
set "DIST_DIR=%PROJECT_DIR%\dist"
set "WORK_DIR=%PROJECT_DIR%\build"

cls
echo [i] Creation de l'executable Windows...
echo.

:: 1) Verification de Python et Git
echo [~] Verification des prerequis...
where python >nul 2>&1
if errorlevel 1 (
  echo [!] ERREUR: Python non trouve !
  echo     https://www.python.org/downloads/
  pause & exit /b 1
)
where git >nul 2>&1
if errorlevel 1 (
  echo [!] ERREUR: Git non trouve !
  echo     https://git-scm.com/download/win
  pause & exit /b 1
)
echo [OK] Prerequis OK.
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
set /p BRANCH="[?] Quelle branche souhaitez-vous packager ? [main] : "
if "%BRANCH%"=="" set BRANCH=main
echo [i] Branche sélectionnée : %BRANCH%
echo.

:: 2) Cloner ou mettre à jour le depot
echo [~] Mise a jour du code source...
if exist "%PROJECT_DIR%" (
  if exist "%PROJECT_DIR%\.git" (
    pushd "%PROJECT_DIR%"
      git fetch
      git checkout %BRANCH%
      if errorlevel 1 (
        echo [!] Impossible de basculer sur la branche %BRANCH% !
        popd & pause & exit /b 1
      )
      git pull
      if errorlevel 1 (
        echo [!] git pull a echoue !
        popd & pause & exit /b 1
      )
    popd
  ) else (
    echo [!] "%PROJECT_DIR%" existe mais n'est PAS un depot Git valide !
    pause & exit /b 1
  )
) else (
  git clone -b %BRANCH% "%REPO_URL%" "%PROJECT_DIR%"
  if errorlevel 1 (
    echo [!] git clone a echoue !
    pause & exit /b 1
  )
)
echo [OK] Code source pret.
echo.

:: 3) Verification du fichier principal
echo [~] Verification du fichier principal...
if not exist "%PROJECT_DIR%\%MAIN_FILE%" (
  echo [!] ERREUR: Le fichier %MAIN_FILE% n'existe pas dans %PROJECT_DIR% !
  pause & exit /b 1
)
echo [OK] Fichier %MAIN_FILE% trouve.
echo.

:: 4) Installation des dependances
echo [~] Installation des dependances...
pushd "%PROJECT_DIR%"
  python -m pip install --upgrade pip >nul 2>&1
  echo     Installation de PyInstaller...
  python -m pip install pyinstaller
  if errorlevel 1 (
    echo [!] ERREUR: Impossible d'installer PyInstaller !
    popd & pause & exit /b 1
  )

  if exist requirements.txt (
    echo     Installation depuis requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
      echo [!] Echec de l'installation des dependances !
      popd & pause & exit /b 1
    )
  ) else (
    echo     Installation de Flask...
    python -m pip install flask
    if errorlevel 1 (
      echo [!] Echec de l'installation de Flask !
      popd & pause & exit /b 1
    )
  )
  echo [OK] Dependances installees.
  echo.

  :: 5) Nettoyage des anciens builds
  echo [~] Nettoyage des anciens builds...
  if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
  if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
  echo [OK] Nettoyage termine.
  echo.

  :: 6) Construction de l'executable
  echo [^>^>^>] Construction de l'executable avec PyInstaller...
  echo.

  pyinstaller --noconfirm --clean --onedir ^
      --add-data "Templates;Templates" ^
      --add-data "Styles;Styles" ^
      --add-data "Functions;Functions" ^
      --add-data "Images;Images" ^
      --add-data "armoire.db;." %MAIN_FILE%

  if exist "%DIST_DIR%\APP\APP.exe" (
    echo.
    echo [OK] Executable cree avec succes !
    echo     Chemin: %DIST_DIR%\APP\APP.exe
  ) else (
    echo.
    echo [!] ERREUR: La creation de l'executable a echoue !
  )
popd
echo.

pause
endlocal
