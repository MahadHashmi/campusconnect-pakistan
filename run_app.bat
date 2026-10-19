@echo off
title CampusConnect Server
color 0A
echo ========================================================
echo       Starting CampusConnect App ^& Server...
echo ========================================================
echo.
echo Local PC Address:   http://127.0.0.1:8000
echo Mobile Phone Link:  http://192.168.1.5:8000
echo.
echo IMPORTANT: Leave this black window OPEN while using the app!
echo.
cd /d "C:\Users\mahad\.gemini\antigravity\scratch\campus_connect_backend"
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000
"C:\Users\mahad\AppData\Local\Programs\Python\Python312\python.exe" -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
