@echo off
setlocal

echo Starting ADAS Functional Safety Simulation Tool setup...

REM Check if virtual environment exists
if not exist "myenv\" (
    echo Virtual environment not found. Creating new environment...
    python -m venv myenv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call myenv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Install requirements
echo Installing required packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements.
    pause
    exit /b 1
)

REM Set PYTHONPATH
echo Setting PYTHONPATH...
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Run the application
echo Starting the application...
python src/main.py
if errorlevel 1 (
    echo Application exited with an error.
    pause
    exit /b 1
)

endlocal