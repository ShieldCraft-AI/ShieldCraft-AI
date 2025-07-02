@echo off
REM List all files and folders up to 3 levels deep.
REM Exclude:
REM - Any folder whose name starts with a period (dot), e.g. .nox, .venv, .github, and their contents.
REM - Any 'node_modules' folders and their contents.
REM Output will be saved to tree.txt in the current directory.

powershell -NoProfile -Command ^
    "$ErrorActionPreference = 'SilentlyContinue'; " ^
    "$root = Get-Location; " ^
    "Get-ChildItem -Recurse -Depth 3 | " ^
    "Where-Object { " ^
    "   -not ($_.FullName -match '(?<![a-zA-Z0-9_])(\.|node_modules)(?=[\\/])') " ^
    "   -and -not ($_.FullName -match '[\\/]\.[^\\/]+([\\/]|$)') " ^
    "   -and -not ($_.FullName -match '[\\/]node_modules([\\/]|$)') " ^
    "} | " ^
    "ForEach-Object { " ^
    "   $rel = $_.FullName.Substring($root.Path.Length + 1); $rel " ^
    "}" > tree.txt

echo Output saved to tree.txt
pause
