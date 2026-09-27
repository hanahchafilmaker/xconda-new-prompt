@echo off
rem ============================================================
rem  XCONDA 편집기 로컬 서버 (Windows용 - make 불필요)
rem
rem  사용법:  engine.bat [포트]     기본 포트: 8080
rem  정지  :  Ctrl+C
rem
rem  열리는 주소:
rem    /            편집기 UI (S8 씬 내장)
rem    /storyboard  글콘티 작업실
rem    /engine      빈 편집기 (씬 JSON 드롭용)
rem    /scene       씬 JSON
rem ============================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"

set "PORT=%~1"
if not defined PORT set "PORT=8080"

rem --- Python 3 찾기: py 런처 > python > python3 ---
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY where python3 >nul 2>nul && set "PY=python3"
if not defined PY (
    echo [오류] Python 3 를 찾을 수 없습니다.
    echo        https://www.python.org/downloads/ 에서 설치한 뒤 다시 실행하세요.
    echo        설치 시 "Add python.exe to PATH" 체크를 권장합니다.
    exit /b 1
)

echo [1/2] 편집기 UI 빌드 (tools\build_editor.py)...
%PY% tools\build_editor.py
if errorlevel 1 (
    echo [오류] 편집기 빌드에 실패했습니다.
    exit /b 1
)

echo.
echo [2/2] 서버 시작 (정지: Ctrl+C)
echo.
echo   편집기     : http://localhost:%PORT%/
echo   글콘티     : http://localhost:%PORT%/storyboard
echo   빈 편집기  : http://localhost:%PORT%/engine
echo   씬 JSON    : http://localhost:%PORT%/scene
echo.
start "" http://localhost:%PORT%/
%PY% tools\serve.py %PORT%
