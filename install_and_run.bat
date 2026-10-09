@echo off
rem File: install_and_run.bat
rem Summary: Forward startup options to START_BUTTON_CLICKER.cmd.
rem Author: 5garashi.com設計事務所 / 5garashi.com Design Office
rem Created: 2026-07-24
rem License: Not specified
rem SPDX-License-Identifier: NOASSERTION
setlocal
if not exist "%~dp0START_BUTTON_CLICKER.cmd" (
    echo ERROR: START_BUTTON_CLICKER.cmd was not found.
    echo Extract all files from the ZIP before starting.
    echo.
    pause
    exit /b 1
)
call "%~dp0START_BUTTON_CLICKER.cmd" %*
endlocal
