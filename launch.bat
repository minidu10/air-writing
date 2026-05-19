@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo No .venv found at %CD%\.venv
    echo First-time setup:
    echo     python -m venv .venv
    echo     .venv\Scripts\activate
    echo     pip install -r requirements.txt
    echo.
    echo Falling back to system Python...
)

python src\main.py %*

if errorlevel 1 (
    echo.
    echo App exited with error code %errorlevel%.
    echo Press any key to close this window.
    pause >nul
)
