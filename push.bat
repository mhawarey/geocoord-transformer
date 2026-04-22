@echo off
setlocal EnableDelayedExpansion

echo ================================
echo   Auto GitHub Push Script
echo ================================

:: Move to script directory
cd /d "%~dp0"

:: Get repo name from folder
for %%I in (.) do set REPONAME=%%~nxI

echo Repo name: %REPONAME%

:: Extract description from README.md (2nd line fallback)
set DESCRIPTION=
if exist README.md (
for /f "skip=1 delims=" %%A in (README.md) do (
set DESCRIPTION=%%A
goto :desc_done
)
)
:desc_done

if "%DESCRIPTION%"=="" (
set DESCRIPTION=%REPONAME%
)

echo Description: %DESCRIPTION%
echo.

:: Init git if needed
if not exist ".git" (
echo Initializing git...
git init
)

:: Add + commit
git add .
git commit -m "%REPONAME%: initial commit" 2>nul

:: Create repo + push
gh repo create %REPONAME% --public --source=. --remote=origin --push --description "%DESCRIPTION%"

echo.
echo DONE: https://github.com/mhawarey/%REPONAME%
pause
endlocal
