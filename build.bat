@echo off
REM Compilation locale FACULTATIVE (nécessite Python sur l'ordinateur).
REM Vous n'en avez pas besoin : GitHub Actions compile le logiciel pour vous.
chcp 65001 >nul
python -m pip install -r requirements.txt
python -m unittest discover -s tests -t . -v
if errorlevel 1 (
  echo Les tests ont échoué. Compilation annulée.
  exit /b 1
)
python -m PyInstaller --noconfirm AutoSaisieWord.spec
if exist dist\AutoSaisieWord.exe (
  echo Compilation réussie : dist\AutoSaisieWord.exe
) else (
  echo La compilation a échoué.
  exit /b 1
)
