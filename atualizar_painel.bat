@echo off
setlocal

cd /d "%~dp0"

set PYEXE=
where python >nul 2>&1 && set PYEXE=python
if not defined PYEXE (
  where py >nul 2>&1 && set PYEXE=py
)
if not defined PYEXE (
  echo ERRO: Python nao foi encontrado no PATH.
  echo Instale o Python em https://www.python.org/downloads/ e tente novamente.
  pause
  exit /b 1
)

%PYEXE% -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
  echo Instalando biblioteca necessaria: openpyxl...
  %PYEXE% -m pip install -r requirements.txt
)

%PYEXE% update_and_publish.py

echo.
pause
