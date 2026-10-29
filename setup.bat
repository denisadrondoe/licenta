@echo off
setlocal
cd /d "%~dp0"

echo.
echo ==================================================
echo   Pregatirea mediului pentru proiectul de licenta
echo ==================================================
echo.

rem --- 1. Gasesc Python ---
set "PY="
python --version >nul 2>nul && set "PY=python"
if not defined PY py --version >nul 2>nul && set "PY=py"
if not defined PY goto :fara_python
echo [1/4] Python gasit:
%PY% --version

rem --- 2. Creez mediul virtual, daca nu exista ---
if exist ".venv\Scripts\python.exe" goto :venv_exista
echo [2/4] Creez mediul virtual .venv ...
%PY% -m venv .venv
if errorlevel 1 goto :eroare_venv
goto :instalare
:venv_exista
echo [2/4] Mediul virtual .venv exista deja.

rem --- 3. Instalez bibliotecile din requirements.txt ---
:instalare
echo [3/4] Instalez bibliotecile din requirements.txt ...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if errorlevel 1 goto :eroare_pip

rem --- 4. Creez fisierul .env, daca nu exista ---
if exist ".env" goto :env_exista
copy ".env.example" ".env" >nul
echo [4/4] Am creat fisierul .env din .env.example.
echo       Deschide-l si completeaza tokenurile si cheia API.
goto :final
:env_exista
echo [4/4] Fisierul .env exista deja - nu l-am modificat.

:final
echo.
echo Gata! Mediul este pregatit.
echo Pentru a lucra, deschide un terminal in acest folder si scrie:
echo     .venv\Scripts\activate
echo.
pause
exit /b 0

:fara_python
echo [EROARE] Python nu este instalat sau nu este in PATH.
echo Instaleaza-l de pe python.org si bifeaza "Add python.exe to PATH".
pause
exit /b 1

:eroare_venv
echo [EROARE] Nu am putut crea mediul virtual.
pause
exit /b 1

:eroare_pip
echo [EROARE] Instalarea bibliotecilor a esuat. Verifica conexiunea la internet
echo si trimite mesajul de eroare de mai sus.
pause
exit /b 1
