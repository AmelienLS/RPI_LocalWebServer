@echo off
REM Construction de l'executable Windows avec PyInstaller
REM Assurez-vous que PyInstaller est installe : pip install pyinstaller

set "MAIN_FILE=APP.py"
set "DIST_DIR=dist"
set "WORK_DIR=build"

pyinstaller --noconfirm --clean --onedir ^
    --add-data "Templates;Templates" ^
    --add-data "Styles;Styles" ^
    --add-data "Functions;Functions" ^
    --add-data "Images;Images" ^
    --add-data "armoire.db;." %MAIN_FILE%

if exist %DIST_DIR%\APP\APP.exe (
    echo.
    echo Exécutable créé dans %DIST_DIR%\APP\APP.exe
) else (
    echo.
    echo Erreur lors de la création de l'exécutable.
)

pause
