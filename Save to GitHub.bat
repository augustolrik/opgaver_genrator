@echo off
setlocal

set "GIT=C:\Python\Tools\PortableGit\cmd\git.exe"

if not exist "%GIT%" (
  echo Git was not found at %GIT%.
  exit /b 1
)

cd /d "%~dp0"

if "%~1"=="" (
  set "MESSAGE=Save project updates"
) else (
  set "MESSAGE=%*"
)

"%GIT%" status --short
"%GIT%" add .
"%GIT%" diff --cached --quiet
if %ERRORLEVEL%==0 (
  echo No changes to commit.
) else (
  "%GIT%" commit -m "%MESSAGE%"
)

"%GIT%" push
