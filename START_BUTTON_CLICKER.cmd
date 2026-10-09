@echo off
rem File: START_BUTTON_CLICKER.cmd
rem Summary: Install dependencies and launch Foreground Button Clicker.
rem Author: 5garashi.com設計事務所 / 5garashi.com Design Office
rem Created: 2026-07-24
rem License: Not specified
rem SPDX-License-Identifier: NOASSERTION
setlocal EnableExtensions
title Foreground Button Clicker - Startup
cd /d "%~dp0"

set "LOG_FILE=%~dp0startup_log.txt"
> "%LOG_FILE%" echo Foreground Button Clicker startup log
>>"%LOG_FILE%" echo Date: %DATE% %TIME%
>>"%LOG_FILE%" echo Folder: %CD%

echo Foreground Button Clicker v1.3.0
echo.

if not exist "foreground_button_clicker.py" (
    echo ERROR: foreground_button_clicker.py was not found.
    echo.
    echo The program was probably started from inside the ZIP file.
    echo Right-click the ZIP, select "Extract All", and start it again.
    >>"%LOG_FILE%" echo ERROR: foreground_button_clicker.py was not found.
    echo.
    echo Startup log: "%LOG_FILE%"
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERROR: requirements.txt was not found.
    echo.
    echo Right-click the ZIP, select "Extract All", and start it again.
    >>"%LOG_FILE%" echo ERROR: requirements.txt was not found.
    echo.
    echo Startup log: "%LOG_FILE%"
    pause
    exit /b 1
)

set "PYTHON_COMMAND="
set "PYTHON_ARGUMENTS="

where py >nul 2>&1
if not errorlevel 1 (
    py -3 --version >>"%LOG_FILE%" 2>&1
    if not errorlevel 1 (
        set "PYTHON_COMMAND=py"
        set "PYTHON_ARGUMENTS=-3"
    )
)

if not defined PYTHON_COMMAND (
    where python >nul 2>&1
    if not errorlevel 1 (
        python --version >>"%LOG_FILE%" 2>&1
        if not errorlevel 1 set "PYTHON_COMMAND=python"
    )
)

if not defined PYTHON_COMMAND (
    where python3 >nul 2>&1
    if not errorlevel 1 (
        python3 --version >>"%LOG_FILE%" 2>&1
        if not errorlevel 1 set "PYTHON_COMMAND=python3"
    )
)

if not defined PYTHON_COMMAND (
    echo ERROR: Python 3 was not found.
    echo Install Python 3 and enable "Add Python to PATH".
    >>"%LOG_FILE%" echo ERROR: Python 3 was not found.
    echo.
    echo Startup log: "%LOG_FILE%"
    pause
    exit /b 1
)

echo [1/2] Checking the required Windows library...
>>"%LOG_FILE%" echo Python command: %PYTHON_COMMAND% %PYTHON_ARGUMENTS%
%PYTHON_COMMAND% %PYTHON_ARGUMENTS% -m pip install --disable-pip-version-check --user -r requirements.txt >>"%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo ERROR: The required library could not be installed.
    echo.
    type "%LOG_FILE%"
    echo.
    echo Startup log: "%LOG_FILE%"
    pause
    exit /b 1
)

echo [2/2] Starting the program...
echo.
%PYTHON_COMMAND% %PYTHON_ARGUMENTS% foreground_button_clicker.py %* >>"%LOG_FILE%" 2>&1
set "PROGRAM_EXIT_CODE=%ERRORLEVEL%"

if not "%PROGRAM_EXIT_CODE%"=="0" (
    echo.
    echo ERROR: The program ended with exit code %PROGRAM_EXIT_CODE%.
    echo.
    type "%LOG_FILE%"
    echo.
    echo Startup log: "%LOG_FILE%"
    pause
    exit /b %PROGRAM_EXIT_CODE%
)

echo.
echo The program has ended normally.
echo Startup log: "%LOG_FILE%"
pause
exit /b 0
