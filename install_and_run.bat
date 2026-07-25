@echo off
setlocal
if not exist "%~dp0START_BUTTON_CLICKER.cmd" (
    echo ERROR: START_BUTTON_CLICKER.cmd was not found.
    echo Extract all files from the ZIP before starting.
    echo.
    pause
    exit /b 1
)
call "%~dp0START_BUTTON_CLICKER.cmd"
endlocal
