@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
    set /p THREE_DS_IP=Enter 3DS IP address: 
) else (
    set "THREE_DS_IP=%~1"
)

if "%THREE_DS_IP%"=="" (
    echo No IP address supplied.
    pause
    exit /b 2
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 test_crystal_vc_battle_state.py %THREE_DS_IP% --watch --raw
) else (
    python test_crystal_vc_battle_state.py %THREE_DS_IP% --watch --raw
)

echo.
pause
