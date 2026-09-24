@echo off
setlocal

cd /d "%~dp0"

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

%PYEXE% -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
  echo Instalando biblioteca necessaria: openpyxl...
  %PYEXE% -m pip install -r requirements.txt
)

%PYEXE% colaborador_server.py

echo.
pause
