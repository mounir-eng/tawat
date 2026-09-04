@echo off
chcp 65001 >nul
title Artisan DZ Pro
cd /d "%~dp0"

echo.
echo ================================================
echo    ARTISAN DZ Pro - demarrage en cours...
echo ================================================
echo.

rem 1) Installation des dependances si besoin
python -m pip install --quiet --disable-pip-version-check -r requirements.txt

rem 2) Ouverture du navigateur sur l'application
start "" http://localhost:8501

rem 3) Demarrage du serveur (laisser cette fenetre ouverte)
rem    Les options d'adresse/port restent EN LIGNE DE COMMANDE : le fichier
rem    .streamlit\config.toml doit rester compatible Streamlit Cloud.
python -m streamlit run streamlit_app.py --server.port 8501 --server.address localhost --server.headless false

pause
