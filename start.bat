@echo off
title FinSight AI — Startup
color 0B

echo.
echo  ============================================================
echo    FinSight AI — Stock Intelligence Platform
echo  ============================================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo  [SETUP] Copying .env.example to .env ...
    copy .env.example .env
    echo  [ACTION] Please edit .env and add your API keys
    echo           GEMINI_API_KEY  - from https://aistudio.google.com
    echo           NEWS_API_KEY    - from https://newsapi.org
    echo.
)

REM Check if virtual environment exists
if not exist "venv" (
    echo  [SETUP] Creating Python virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo  [START] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo  [INSTALL] Installing dependencies...
pip install -r backend\requirements.txt --quiet

REM Download TextBlob corpus
echo  [SETUP] Downloading NLP data...
python -c "import nltk; nltk.download('punkt', quiet=True)" 2>nul
python -c "from textblob import TextBlob; TextBlob('test').sentiment" 2>nul

echo.
echo  ============================================================
echo    Starting FinSight AI Server...
echo    Open your browser at: http://127.0.0.1:5000
echo  ============================================================
echo.

REM Start Flask
cd backend
python app.py

pause
