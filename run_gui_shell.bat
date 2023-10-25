REM @ECHO OFF
echo Current path: %CD%
for /f "delims=" %%a  IN ('python -m pipenv --venv') DO set VENV_PATH=%%a
echo Virtual env path: %VENV_PATH%
%VENV_PATH%\Scripts\python.exe ui.py
if ERRORLEVEL 1 PAUSE
