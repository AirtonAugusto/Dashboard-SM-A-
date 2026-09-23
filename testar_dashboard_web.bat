@echo off
setlocal

cd /d "%~dp0backend"

set PYEXE=
py --version >nul 2>&1
if not errorlevel 1 set PYEXE=py

if not defined PYEXE (
  python --version >nul 2>&1
  if not errorlevel 1 set PYEXE=python
)

if not defined PYEXE (
  echo ERRO: Python nao foi encontrado.
  echo Instale o Python em https://www.python.org/downloads/ e tente novamente.
  pause
  exit /b 1
)

echo Instalando dependencias (so demora na primeira vez)...
%PYEXE% -m pip install -q -r requirements.txt

%PYEXE% testar_local.py

pause
