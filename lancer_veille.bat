@echo off
REM Lanceur pour le Planificateur de taches Windows.
REM Demarrer dans : le dossier du projet.
cd /d "%~dp0"
call venv\Scripts\activate.bat
python scraper.py
