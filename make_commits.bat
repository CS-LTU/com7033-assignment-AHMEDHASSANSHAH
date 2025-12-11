@echo off
setlocal enabledelayedexpansion

REM Navigate to project directory
cd /d "f:\LTU\1 SECURE SOFTWARE DEVELOPMENT\ASS V3\stroke-prediction-app"

REM Check current status
echo Current git status:
git status

REM Make commit 1
echo.
echo Making Commit 1: Initial project setup
git commit -m "commit 1: Initial project structure with Flask and database configuration"

REM Make commit 2
echo.
echo Making Commit 2: Security and validation implementation
git commit -m "commit 2: Implement input validation, password hashing, and error logging"

REM Make commit 3
echo.
echo Making Commit 3: Patient CRUD and MongoDB integration
git commit -m "commit 3: Add patient CRUD operations with MongoDB and authentication routes"

REM Make commit 4
echo.
echo Making Commit 4: Web interface and testing
git commit -m "commit 4: Complete HTML templates, unit tests, and data seeding functionality"

REM Show commit history
echo.
echo Final commit history:
git log --oneline
