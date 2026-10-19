@echo off
title CampusConnect Mobile Link (Cloudflare)
color 0B
echo ========================================================
echo       Generating Public Mobile Link for Phone...
echo ========================================================
echo.
echo Make sure "run_app.bat" is running in another window!
echo.
echo Connecting to Cloudflare secure tunnel...
echo Copy the "https://....trycloudflare.com" link below
echo and open it on your phone (or send it to your WhatsApp)!
echo.
"C:\Users\mahad\AppData\Local\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe" tunnel --url http://127.0.0.1:8000
pause
