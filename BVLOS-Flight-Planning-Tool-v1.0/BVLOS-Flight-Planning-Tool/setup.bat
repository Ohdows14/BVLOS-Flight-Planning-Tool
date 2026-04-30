@echo off
REM BVLOS Flight Planning Tool - Windows Setup Script

echo ==================================
echo BVLOS Flight Planning Tool Setup
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

echo Python detected
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ==================================
echo Setup complete!
echo ==================================
echo.
echo Next steps:
echo 1. Add your data files to data\ folders
echo 2. Activate environment: venv\Scripts\activate
echo 3. Run the app: streamlit run app.py
echo.
pause
