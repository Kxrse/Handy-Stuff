@echo off
echo Creating file tree...
cd /d "%~dp0"
tree /F /A > "%~dp0file_tree.txt"
if exist "%~dp0file_tree.txt" (
    echo SUCCESS: file_tree.txt created in %~dp0
) else (
    echo ERROR: Failed to create file
)
pause