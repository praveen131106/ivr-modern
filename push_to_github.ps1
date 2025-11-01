# PowerShell script to push to GitHub
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Train IVR System - GitHub Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Git
$gitFound = $false
$gitPath = $null

# Check if git is in PATH
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Git found in PATH" -ForegroundColor Green
        Write-Host $gitVersion -ForegroundColor Gray
        $gitFound = $true
    }
} catch {
    Write-Host "[INFO] Git not in PATH, checking common locations..." -ForegroundColor Yellow
    
    # Check common Git installation paths
    $possiblePaths = @(
        "C:\Program Files\Git\bin\git.exe",
        "C:\Program Files (x86)\Git\bin\git.exe",
        "$env:LOCALAPPDATA\Programs\Git\cmd\git.exe",
        "$env:ProgramFiles\Git\cmd\git.exe"
    )
    
    foreach ($path in $possiblePaths) {
        if (Test-Path $path) {
            Write-Host "[OK] Found Git at: $path" -ForegroundColor Green
            $gitDir = Split-Path $path -Parent
            $env:PATH = "$gitDir;$env:PATH"
            try {
                $gitVersion = & $path --version
                Write-Host $gitVersion -ForegroundColor Gray
                $gitFound = $true
                break
            } catch {
                continue
            }
        }
    }
}

if (-not $gitFound) {
    Write-Host ""
    Write-Host "[ERROR] Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git from one of these options:" -ForegroundColor Yellow
    Write-Host "1. Download: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. Or use GitHub Desktop: https://desktop.github.com/" -ForegroundColor White
    Write-Host ""
    Write-Host "After installing Git, run this script again." -ForegroundColor Yellow
    Write-Host ""
    $response = Read-Host "Would you like me to open the Git download page? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Start-Process "https://git-scm.com/download/win"
    }
    exit 1
}

Write-Host ""
Write-Host "[INFO] Repository: https://github.com/praveen131106/AI-conv-train-ivr" -ForegroundColor Cyan
Write-Host ""

# Initialize git if needed
if (-not (Test-Path .git)) {
    Write-Host "[INFO] Initializing git repository..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to initialize git" -ForegroundColor Red
        exit 1
    }
}

# Configure remote
Write-Host "[INFO] Configuring remote repository..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/praveen131106/AI-conv-train-ivr.git
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Remote configuration issue (may already exist)" -ForegroundColor Yellow
}

# Configure user
git config user.name "Praveen" 2>$null
git config user.email "praveen131106@users.noreply.github.com" 2>$null

# Stage files
Write-Host ""
Write-Host "[INFO] Staging all files..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to stage files" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Files staged" -ForegroundColor Green

# Commit
Write-Host ""
Write-Host "[INFO] Creating commit..." -ForegroundColor Yellow
$commitMessage = @"
Complete Train IVR System Implementation

- Full backend with FastAPI
- Advanced NLP engine with intent recognition
- Voice control with Web Speech API
- All 10+ service flows operational
- Professional UI/UX
- Complete documentation
- Error handling and recovery
- Session management
- Call logging and transcripts
"@

git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] No changes to commit or commit skipped" -ForegroundColor Yellow
} else {
    Write-Host "[OK] Commit created" -ForegroundColor Green
}

# Set branch
Write-Host ""
Write-Host "[INFO] Setting branch to main..." -ForegroundColor Yellow
git branch -M main

# Push
Write-Host ""
Write-Host "[INFO] Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "[NOTE] You may be prompted for GitHub credentials" -ForegroundColor Cyan
Write-Host ""

git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Code pushed to GitHub!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Repository URL:" -ForegroundColor Cyan
    Write-Host "https://github.com/praveen131106/AI-conv-train-ivr" -ForegroundColor White
    Write-Host ""
    Write-Host "You can now view your code on GitHub!" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "  Push encountered an issue" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Possible solutions:" -ForegroundColor Cyan
    Write-Host "1. Authentication:" -ForegroundColor White
    Write-Host "   - Use GitHub Personal Access Token as password" -ForegroundColor Gray
    Write-Host "   - Generate token: GitHub → Settings → Developer settings → Personal access tokens" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. If conflicts exist:" -ForegroundColor White
    Write-Host "   git pull origin main --allow-unrelated-histories" -ForegroundColor Gray
    Write-Host "   Then run this script again" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Manual push:" -ForegroundColor White
    Write-Host "   git push -u origin main --force" -ForegroundColor Gray
    Write-Host "   (Use with caution - will overwrite remote files)" -ForegroundColor Yellow
    Write-Host ""
}

