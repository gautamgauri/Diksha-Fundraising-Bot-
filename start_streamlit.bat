@echo off
REM Diksha Fundraising MVP - Streamlit Windows Startup Script
REM Configures UTF-8 encoding and starts the Streamlit application

echo Starting Diksha Fundraising Streamlit App...
echo.

REM Set UTF-8 console encoding for emoji support
chcp 65001 >nul

REM Set UTF-8 environment variables
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

REM Check if virtual environment exists
if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found. Running with system Python...
)

echo.
echo 🚀 Starting Streamlit app with UTF-8 support...
echo 📱 App will open in your browser automatically
echo 🛑 Press Ctrl+C to stop
echo.

cd streamlit-app
streamlit run streamlit_app.py

pause