@echo off
setlocal
cd /d "%~dp0\..\.."

if not exist "pokebot\common\luma_input.py" (
    echo ERROR: pokebot\common\luma_input.py was not found.
    echo.
    echo If you downloaded only the hotfix folder, copy APPLY_HOTFIX.bat and
    echo apply_hotfix.py into the ROOT of your Pokebot3DS-CFW v0p42Z folder,
    echo then run APPLY_HOTFIX.bat there.
    echo.
    pause
    exit /b 2
)

where py >nul 2>nul
if not errorlevel 1 (
    py -3 "hotfixes\v0p42Z_input_status_recovery\apply_hotfix.py"
) else (
    python "hotfixes\v0p42Z_input_status_recovery\apply_hotfix.py"
)

set ERR=%ERRORLEVEL%
echo.
if not "%ERR%"=="0" echo Hotfix failed with exit code %ERR%.
pause
exit /b %ERR%
