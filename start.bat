@echo off
echo Starting Viel-AI setup and launch...
echo.

REM Go to the project folder
set "PROJECT_DIR=%USERPROFILE%\Documents\viel-ai"
cd /d "%PROJECT_DIR%"

REM Check for main.py
if not exist "main.py" (
    echo Error: main.py not found in %PROJECT_DIR%.
    echo Please run the viel_installer.bat script first.
    pause
    exit /b 1
)

REM Find python 3.10 explicitly (if multiple versions are installed)
for /f "delims=" %%p in ('where python') do (
    call :check_version "%%p"
    if %found310%==1 (
        set "PYTHON_EXE=%%p"
        goto :venv_setup
    )
)

echo Error: Python 3.10 not found.
echo Please ensure Python 3.10 is installed correctly.
pause
exit /b 1

:check_version
set "found310=0"
for /f "tokens=2 delims== " %%v in ('%~1 --version 2^>nul') do (
    echo %%v | findstr "3.10" >nul && set found310=1
)
exit /b

:venv_setup
REM Set up virtual environment
echo Setting up Python 3.10 virtual environment...
if not exist "venv" (
    echo Creating new virtual environment using: %PYTHON_EXE%
    "%PYTHON_EXE%" -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

REM Activate the virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.
echo.

REM Check if uv is installed in the virtual environment
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

REM Check for requirements
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
set "ERRORLEVEL=%ERRORLEVEL%"

echo.
echo main.py exited with code: %ERRORLEVEL%
echo Press any key to continue...
pause >nul

REM Deactivate venv after done
call venv\Scripts\deactivate.bat
echo Virtual environment deactivated.

echo.
echo Application execution completed.
pause
