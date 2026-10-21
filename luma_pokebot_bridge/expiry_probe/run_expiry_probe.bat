@echo off
cd /d "%~dp0"
echo INPUT EXPIRY TEST - L shoulder only, no walking
echo Open Alpha Sapphire in the overworld and enable both Pokebot bridges.
echo Default 3DS IP: 192.168.1.20
py -3 expiry_probe.py %*
echo.
pause
