@echo off
setlocal
cd /d "%~dp0"
set "PATH=C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin;%PATH%"
set "NODE_COMPILE_CACHE=%~dp0.cache\node-compile-cache"
call "C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\bin\fallback\pnpm.cmd" build
if errorlevel 1 exit /b %errorlevel%
type nul > docs\.nojekyll
endlocal