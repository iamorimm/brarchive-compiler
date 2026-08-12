@echo off
title Brarchive Compiler
if not exist brarchive-compiler.py (
    echo [ERROR] brarchive-compiler.py not found!
    echo.
    pause
    exit /b 1
)
echo.
python brarchive-compiler.py

if errorlevel 1 (
    echo.
    echo [ERROR] Compilation failed!
) else (
    echo.
    echo [OK] Compilation completed!
)

echo.
pause