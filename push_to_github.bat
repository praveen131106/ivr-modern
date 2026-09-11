@echo off
echo ========================================
echo  Train IVR System - GitHub Push Script
echo ========================================
echo.
echo This script will push your code to:
echo https://github.com/praveen131106/AI-conv-train-ivr
echo.

REM Check if git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH!
    echo.
    echo Please install Git from: https://git-scm.com/download/win
    echo After installation, restart this script.
    echo.
    pause
    exit /b 1
)

echo [OK] Git found
git --version
echo.

REM Check if already a git repo
if exist .git (
    echo [INFO] Git repository already initialized
) else (
    echo [INFO] Initializing git repository...
    git init
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to initialize git repository
        pause
        exit /b 1
    )
)

REM Add remote repository
echo.
echo [INFO] Configuring remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/praveen131106/AI-conv-train-ivr.git
if %errorlevel% neq 0 (
    echo [WARNING] Remote may already exist, continuing...
)

REM Configure git user (if not set)
git config user.name "Praveen" >nul 2>&1
git config user.email "praveen131106@users.noreply.github.com" >nul 2>&1

echo.
echo [INFO] Staging all files...
git add .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to stage files
    pause
    exit /b 1
)

echo [OK] Files staged
echo.

echo [INFO] Creating commit...
git commit -m "Complete Train IVR System Implementation

- Full backend with FastAPI
- Advanced NLP engine with intent recognition  
- Voice control with Web Speech API
- All 10+ service flows operational
- Professional UI/UX
- Complete documentation
- Error handling and recovery
- Session management
- Call logging and transcripts" 2>nul

if %errorlevel% neq 0 (
    echo [INFO] No changes to commit or commit skipped
) else (
    echo [OK] Commit created
)

echo.
echo [INFO] Setting branch to main...
git branch -M main

echo.
echo [INFO] Pushing to GitHub...
echo [NOTE] You may be prompted for GitHub credentials
echo.

git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo  SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo Repository URL:
    echo https://github.com/praveen131106/AI-conv-train-ivr
    echo.
    echo You can now view your code on GitHub!
    echo.
) else (
    echo.
    echo ========================================
    echo  Push encountered an issue
    echo ========================================
    echo.
    echo Possible solutions:
    echo 1. If authentication failed:
    echo    - Use GitHub Personal Access Token as password
    echo    - Or use GitHub Desktop application
    echo.
    echo 2. If conflicts exist:
    echo    git pull origin main --allow-unrelated-histories
    echo    Then run this script again
    echo.
    echo 3. For first-time push with existing repo:
    echo    git push -u origin main --force
    echo    (Use with caution!)
    echo.
)

pause
