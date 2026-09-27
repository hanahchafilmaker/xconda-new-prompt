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

rem --- Python 3 찾기: 후보를 직접 실행해 보고 실제 동작하는 것을 고른다 ---
rem     (PATH 에 있는 python 이 손상되어 "Unable to create process" 오류를
rem      내는 경우를 걸러낸다)
set "PY="
call :try_python "py -3"   && goto :python_found
call :try_python "py"      && goto :python_found
call :try_python "python"  && goto :python_found
call :try_python "python3" && goto :python_found

echo [오류] 실행 가능한 Python 3 를 찾을 수 없습니다.
echo        설치된 python 이 손상되었을 가능성이 있습니다. 아래 순서로 해결하세요.
echo.
echo        1. 새 Python 설치 관리자를 쓰고 있다면:
echo              py list            설치된 런타임 목록 확인
echo              py install 3.14    런타임 다시 내려받기
echo              py -3 --version    동작 확인
echo.
echo        2. 그래도 안 되면 정식 설치 관리자로 재설치:
echo              https://www.python.org/downloads/
echo              설치 화면에서 "Add python.exe to PATH" 체크 권장
echo.
echo        참고: 서버 없이 편집기 화면만 보려면 index.html 을 더블클릭해도 된다.
exit /b 1

:python_found
echo 사용할 Python: %PY%
echo.
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
exit /b 0

:try_python
rem 인자로 받은 명령이 실제로 Python 을 실행할 수 있는지 검사한다.
rem 실패하면 1, 성공하면 PY 를 설정하고 0 을 반환한다.
%~1 -c "import sys" >nul 2>nul
if errorlevel 1 exit /b 1
set "PY=%~1"
exit /b 0
