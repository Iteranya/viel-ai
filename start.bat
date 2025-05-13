@echo off
echo Starting Viel-AI setup and launch...
echo.

REM Check if we're in the viel-ai directory, if not try to navigate there
if not exist "main.py" (
    if exist "viel-ai" (
        cd viel-ai
    ) else (
        echo Error: viel-ai directory not found.
        echo Please run the setup_viel_ai.bat script first to clone the repository.
        pause
        exit /b 1
    )
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed.
    echo Please run the setup_viel_ai.bat script first to install Python.
    pause
    exit /b 1
)

REM Set up virtual environment
echo Setting up Python virtual environment...
if not exist "venv" (
    echo Creating new virtual environment...
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.
echo.

REM Check if uv is installed in the virtual environment, if not install it
pip show uv >nul 2>&1
if %errorlevel% neq 0 (
    echo UV package installer not found. Installing UV...
    pip install uv
    echo UV installed successfully.
    echo.
) else (
    echo UV is already installed.
    echo.
)

REM Check if requirements.txt exists
if exist "requirements.txt" (
    echo Installing project requirements using UV...
    uv pip install -r requirements.txt
    echo Requirements installed successfully.
    echo.
) else (
    echo Warning: requirements.txt not found.
)

REM Run the main.py file
echo Starting Viel-AI application...
echo.
echo ---------------------------------------------
echo Running main.py
echo ---------------------------------------------
echo.

python main.py

REM Deactivate virtual environment when done
call venv\Scripts\deactivate.bat
echo Virtual environment deactivated.

echo.
echo Application execution completed.
pause