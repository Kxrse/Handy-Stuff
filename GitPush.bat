@echo off
setlocal enabledelayedexpansion
cd /d "C:\Users\Kxrse\Desktop\Kxrse\Personal_Scripts"
set /p msg=Commit message: 
git add .
git commit -m "!msg!"
git push
echo.
echo HANDY-STUFF // REPO UPDATED
pause