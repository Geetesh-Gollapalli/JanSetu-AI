@echo off
title JanSetu AI Launcher
echo ========================================================
echo   JANSETU AI (जनसेतु) - Starting National Platform
echo ========================================================
echo.
echo Running Automated Test Suite...
python tests\test_pipeline.py
echo.
echo National Infrastructure Status:
python cli.py status
echo.
echo Starting Web Dashboard on http://localhost:8080 ...
echo Press Ctrl+C in this window when you want to stop the server.
echo.
start http://localhost:8080
python server\app.py 8080
pause