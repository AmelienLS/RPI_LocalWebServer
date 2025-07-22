@echo off
chcp 65001 >nul
setlocal

:: Variables
set "MAIN_FILE=APP.py"
set "DIST_DIR=dist"
set "WORK_DIR=build"

cls
echo [i] Creation de l'executable Windows...
echo.

:: 1) Verification de Python
echo [~] Verification de Python...
where python >nul 2>&1
if errorlevel 1 (
  echo [!] ERREUR: Python non trouve !
  echo     https://www.python.org/downloads/
  pause & exit /b 1
)
echo [OK] Python trouve.
echo.

:: 2) Verification et installation de pip
echo [~] Verification de pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
  echo [~] Installation de pip...
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  python get-pip.py
  if errorlevel 1 (
    echo [!] ERREUR: Impossible d'installer pip !
    if exist get-pip.py del get-pip.py
    pause & exit /b 1
  )
  if exist get-pip.py del get-pip.py
  echo [OK] pip installe.
) else (
  echo [OK] pip est deja installe.
)
echo.

:: 3) Installation des dependances
echo [~] Installation des dependances...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install pyinstaller
if errorlevel 1 (
  echo [!] ERREUR: Impossible d'installer PyInstaller !
  pause & exit /b 1
)

if exist requirements.txt (
  echo     Installation depuis requirements.txt...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo [!] Echec de l'installation des dependances !
    pause & exit /b 1
  )
) else (
  echo     Installation de Flask...
  python -m pip install flask
  if errorlevel 1 (
    echo [!] Echec de l'installation de Flask !
    pause & exit /b 1
  )
)
echo [OK] Dependances installees.
echo.

:: 4) Nettoyage des anciens builds
echo [~] Nettoyage des anciens builds...
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%WORK_DIR%" rmdir /s /q "%WORK_DIR%"
echo [OK] Nettoyage termine.
echo.

:: 5) Construction de l'executable
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
  echo     Chemin: %CD%\%DIST_DIR%\APP\APP.exe
) else (
  echo.
  echo [!] ERREUR: La creation de l'executable a echoue !
)
echo.

pause
endlocal
