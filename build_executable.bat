@echo off
REM Script pour compiler l'application Password Toolkit Pro en un .exe unique.

echo Nettoyage des anciennes builds...
REM Les commandes 'rd' (rmdir) peuvent echouer si les dossiers n'existent pas, c'est normal.
rd /s /q build 2>nul
rd /s /q dist 2>nul
del "*.spec" 2>nul

echo.
echo Lancement de la compilation avec PyInstaller...
echo Cela peut prendre quelques minutes.

pyinstaller --name "PasswordToolkitPro" ^
    --onefile ^
    --windowed ^
    --icon="assets/icon.ico" ^
    src/main.py

echo.
echo =======================================================
echo  Compilation terminee !
echo.
echo  mon executable 'PasswordToolkitPro.exe' se trouve
echo  dans le dossier 'dist'.
echo =======================================================
echo.
pause
