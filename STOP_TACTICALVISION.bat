@echo off

title Stop TacticalVision

echo.
echo Stopping TacticalVision...
echo.

taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

echo.
echo TacticalVision stopped.
echo.

timeout /t 2 /nobreak >nul

exit