@echo off
echo INFO: Checking for Python 3 and pip...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python could not be found. Please install Python 3 and ensure it's added to your PATH.
    goto :eof
)

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: pip could not be found. Please ensure pip is installed for your Python 3 environment.
    goto :eof
)

echo INFO: Python and pip found.
echo INFO: Attempting to install dependencies from requirements.txt...

REM Create a virtual environment (recommended)
if not exist venv (
    echo INFO: Creating virtual environment 'venv'...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment.
        goto :eof
    )
)

echo INFO: Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo WARNING: Failed to activate virtual environment automatically.
    echo Please activate it manually in your command prompt: venv\Scripts\activate.bat
    REM Continue with global install if activation fails, but warn
)

REM Install dependencies
echo INFO: Installing dependencies, please wait...
python -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo SUCCESS: Dependencies installed successfully.
    echo INFO: If a virtual environment was activated or created, it should be active in this window.
    echo INFO: To run the application: python ei_assistant.py
) else (
    echo.
    echo ERROR: Failed to install some or all dependencies. Please check the output above for errors.
    echo INFO: Make sure you have the necessary build tools if errors occur (e.g., Microsoft Visual C++ Build Tools for some packages).
)

echo.
REM The virtual environment remains active in the current CMD window until it's closed or 'deactivate' is run.