@echo off
REM Lanceur Windows pour le système multi-agent via WSL
REM Utilise WSL pour exécuter Python depuis Windows

echo =========================================================
echo 🤖 SYSTÈME MULTI-AGENT - KACM QUALCOMM
echo Lanceur Windows (via WSL)
echo =========================================================

REM Vérifier que WSL est disponible
wsl --version >nul 2>&1
if errorlevel 1 (
    echo ❌ WSL n'est pas disponible
    echo Veuillez installer WSL : https://docs.microsoft.com/fr-fr/windows/wsl/install
    pause
    exit /b 1
)

echo ✅ WSL détecté

REM Naviguer vers le répertoire du projet
set PROJECT_DIR=/mnt/c/Users/chaki/Desktop/hackathon/KACM-Qualcomm-track/mcp

REM Afficher le menu
echo.
echo 🎮 MENU DE DÉMONSTRATION
echo =========================================================
echo 1. 🚀 Démonstration automatique (recommandé)
echo 2. 🖥️ Interface desktop (si GUI disponible)
echo 3. 📱 Interface console (toujours disponible)
echo 4. 🧪 Tests système
echo 5. 🔧 Installation/Setup
echo 6. ❓ Aide
echo q. Quitter
echo =========================================================

:menu
set /p choice="Votre choix: "

if "%choice%"=="1" goto auto
if "%choice%"=="2" goto desktop
if "%choice%"=="3" goto console
if "%choice%"=="4" goto test
if "%choice%"=="5" goto setup
if "%choice%"=="6" goto help
if "%choice%"=="q" goto quit
if "%choice%"=="Q" goto quit

echo ❌ Choix invalide
goto menu

:auto
echo 🚀 Lancement automatique...
wsl -e bash -c "cd %PROJECT_DIR% && python3 smart_launcher.py auto"
goto end

:desktop
echo 🖥️ Lancement interface desktop...
wsl -e bash -c "cd %PROJECT_DIR% && python3 desktop_app_simple.py"
goto end

:console
echo 📱 Lancement interface console...
wsl -e bash -c "cd %PROJECT_DIR% && python3 demo_console.py"
goto end

:test
echo 🧪 Lancement des tests...
wsl -e bash -c "cd %PROJECT_DIR% && python3 test_system.py"
goto end

:setup
echo 🔧 Installation/Setup...
wsl -e bash -c "cd %PROJECT_DIR% && python3 setup_windows.py"
goto end

:help
echo 📖 Affichage de l'aide...
wsl -e bash -c "cd %PROJECT_DIR% && cat README_DEMO.md"
goto end

:quit
echo 👋 Au revoir!
goto end

:end
echo.
echo =========================================================
echo 🎉 Merci d'avoir testé le système multi-agent!
echo =========================================================
pause
exit /b 0
