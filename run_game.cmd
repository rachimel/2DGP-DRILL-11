@echo off
setlocal
pushd "%~dp0"
set "DRILL_PYTHON=%USERPROFILE%\miniconda3\envs\game2d\python.exe"
if exist "%DRILL_PYTHON%" (
    "%DRILL_PYTHON%" main.py
) else (
    python main.py
)
if errorlevel 1 pause
popd
endlocal
