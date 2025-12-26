@echo off
REM 🔥 设置 UTF-8 编码
chcp 65001 >nul

REM 🔥 获取完整 Python 路径
for /f "delims=" %%i in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%i"

REM 如果获取失败，尝试 python3
if "%PYTHON_EXE%"=="" (
    for /f "delims=" %%i in ('python3 -c "import sys; print(sys.executable)" 2^>nul') do set "PYTHON_EXE=%%i"
)

REM 如果还是失败，使用默认
if "%PYTHON_EXE%"=="" (
    set "PYTHON_EXE=python"
)

REM 测试是否能导入 Flask
"%PYTHON_EXE%" -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    goto python_error
)

echo [INFO] 使用 Python: %PYTHON_EXE%
goto python_ok

:python_error
cls
echo =========================================
echo   [ERROR] Python 环境缺少依赖
echo =========================================
echo.
echo 当前 Python: %PYTHON_EXE%
echo.
echo 请运行以下命令安装依赖：
echo.
echo   "%PYTHON_EXE%" -m pip install -r translator_api\requirements.txt
echo   "%PYTHON_EXE%" -m pip install -r ocr\requirements.txt
echo   "%PYTHON_EXE%" -m pip install -r inpaint\requirements.txt
echo.
echo =========================================
pause
exit /b 1

:python_ok
REM 🔥 加载环境变量
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1"=="#" set "%%a=%%b"
    )
)

REM 🔥 设置默认值（使用新端口）
if not defined API_PORT set API_PORT=5002
if not defined OCR_PORT set OCR_PORT=8899
if not defined INPAINT_PORT set INPAINT_PORT=8900
if not defined FRONTEND_PORT set FRONTEND_PORT=5001

REM 🔥 设置环境变量（全局）
set PYTHONIOENCODING=utf-8
set NO_PROXY=localhost,127.0.0.1,::1

REM 🔥 获取脚本所在目录（自动适配任意路径）
set "SCRIPT_DIR=%~dp0"
REM 移除末尾的反斜杠
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

:menu
cls
echo =========================================
echo      翻译服务管理菜单 (开发模式)
echo =========================================
echo.
echo   Python: %PYTHON_EXE%
echo   OCR端口: %OCR_PORT%
echo   Inpaint端口: %INPAINT_PORT%
echo   API端口: %API_PORT%
echo   前端端口: %FRONTEND_PORT%
echo.
echo =========================================
echo   1. 启动所有服务
echo   2. 停止所有服务
echo   3. 重启所有服务
echo   4. 查看服务状态
echo   5. 健康检查
echo   6. 查看日志文件
echo   7. 打开服务页面
echo   8. 停止单个服务
echo   9. 重启单个服务
echo   0. 退出
echo =========================================
echo.

set /p choice=请选择操作 (0-9): 

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto health
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto open_urls
if "%choice%"=="8" goto stop_single
if "%choice%"=="9" goto restart_single
if "%choice%"=="0" exit

echo 无效选择，请重新输入！
timeout /t 2 >nul
goto menu

:start
cls
echo.
echo 正在启动所有服务...
echo 使用 Python: %PYTHON_EXE%
echo.

cd /d "%SCRIPT_DIR%"
if not exist "logs" mkdir logs

echo [1/4] 启动 OCR 服务 (%OCR_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && set OCR_PORT=%OCR_PORT% && cd /d "%SCRIPT_DIR%\ocr" && "%PYTHON_EXE%" app.py > "%SCRIPT_DIR%\logs\ocr.log" 2>&1"
timeout /t 3 >nul

echo [2/4] 启动 Inpaint 服务 (%INPAINT_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && set INPAINT_PORT=%INPAINT_PORT% && cd /d "%SCRIPT_DIR%\inpaint" && "%PYTHON_EXE%" app.py > "%SCRIPT_DIR%\logs\inpaint.log" 2>&1"
timeout /t 3 >nul

echo [3/4] 启动 API 服务 (%API_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && set API_PORT=%API_PORT% && cd /d "%SCRIPT_DIR%\translator_api" && "%PYTHON_EXE%" app.py > "%SCRIPT_DIR%\logs\api.log" 2>&1"
timeout /t 3 >nul

echo [4/4] 启动前端服务 (%FRONTEND_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && cd /d "%SCRIPT_DIR%\translator_frontend" && "%PYTHON_EXE%" -m http.server %FRONTEND_PORT% > "%SCRIPT_DIR%\logs\frontend.log" 2>&1"

echo.
echo ✅ 所有服务启动命令已发送！
echo.
echo 等待 5 秒后检查状态...
timeout /t 5 >nul

REM 自动检查状态
echo.
echo 服务状态检查:
netstat -ano | findstr ":%OCR_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ OCR服务 ^(%OCR_PORT%^): 已启动
) else (
    echo ❌ OCR服务 ^(%OCR_PORT%^): 启动失败，请查看日志
)

netstat -ano | findstr ":%INPAINT_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Inpaint服务 ^(%INPAINT_PORT%^): 已启动
) else (
    echo ❌ Inpaint服务 ^(%INPAINT_PORT%^): 启动失败，请查看日志
)

netstat -ano | findstr ":%API_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ API服务 ^(%API_PORT%^): 已启动
) else (
    echo ❌ API服务 ^(%API_PORT%^): 启动失败，请查看日志
)

netstat -ano | findstr ":%FRONTEND_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 前端服务 ^(%FRONTEND_PORT%^): 已启动
) else (
    echo ❌ 前端服务 ^(%FRONTEND_PORT%^): 启动失败，请查看日志
)

echo.
echo 访问地址:
echo   前端:     http://localhost:%FRONTEND_PORT%
echo.
pause
goto menu

:stop
cls
echo.
echo 正在停止所有服务...
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%OCR_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%INPAINT_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%API_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo.
echo ✅ 所有服务已停止！
echo.
pause
goto menu

:status
cls
echo.
echo =========================================
echo   服务状态
echo =========================================
echo.

netstat -ano | findstr ":%OCR_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ OCR服务 ^(%OCR_PORT%^): 运行中
) else (
    echo ❌ OCR服务 ^(%OCR_PORT%^): 未运行
)

netstat -ano | findstr ":%INPAINT_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Inpaint服务 ^(%INPAINT_PORT%^): 运行中
) else (
    echo ❌ Inpaint服务 ^(%INPAINT_PORT%^): 未运行
)

netstat -ano | findstr ":%API_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ API服务 ^(%API_PORT%^): 运行中
) else (
    echo ❌ API服务 ^(%API_PORT%^): 未运行
)

netstat -ano | findstr ":%FRONTEND_PORT%.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 前端服务 ^(%FRONTEND_PORT%^): 运行中
) else (
    echo ❌ 前端服务 ^(%FRONTEND_PORT%^): 未运行
)

echo.
echo =========================================
echo.
pause
goto menu

:logs
cls
cd /d "%SCRIPT_DIR%"
echo.
echo 选择要查看的日志:
echo   1. OCR服务
echo   2. Inpaint服务
echo   3. API服务
echo   4. 前端服务
echo   5. 返回主菜单
echo.
set /p log_choice=请选择 (1-5): 

if "%log_choice%"=="5" goto menu

if "%log_choice%"=="1" (
    if exist "logs\ocr.log" (
        cls
        echo ========== OCR服务日志 (最后50行) ==========
        echo.
        powershell -command "Get-Content '%SCRIPT_DIR%\logs\ocr.log' -Tail 50 -Encoding UTF8"
        echo.
    ) else (
        echo.
        echo ❌ 日志文件不存在: logs/ocr.log
        echo.
    )
    pause
    goto logs
)

if "%log_choice%"=="2" (
    if exist "logs\inpaint.log" (
        cls
        echo ========== Inpaint服务日志 (最后50行) ==========
        echo.
        powershell -command "Get-Content '%SCRIPT_DIR%\logs\inpaint.log' -Tail 50 -Encoding UTF8"
        echo.
    ) else (
        echo.
        echo ❌ 日志文件不存在: logs/inpaint.log
        echo.
    )
    pause
    goto logs
)

if "%log_choice%"=="3" (
    if exist "logs\api.log" (
        cls
        echo ========== API服务日志 (最后50行) ==========
        echo.
        powershell -command "Get-Content '%SCRIPT_DIR%\logs\api.log' -Tail 50 -Encoding UTF8"
        echo.
    ) else (
        echo.
        echo ❌ 日志文件不存在: logs/api.log
        echo.
    )
    pause
    goto logs
)

if "%log_choice%"=="4" (
    if exist "logs\frontend.log" (
        cls
        echo ========== 前端服务日志 (最后50行) ==========
        echo.
        powershell -command "Get-Content '%SCRIPT_DIR%\logs\frontend.log' -Tail 50 -Encoding UTF8"
        echo.
    ) else (
        echo.
        echo ❌ 日志文件不存在: logs/frontend.log
        echo.
    )
    pause
    goto logs
)

echo.
echo ❌ 无效选择！
timeout /t 2 >nul
goto logs

:health
cls
echo.
echo =========================================
echo   健康检查
echo =========================================
echo.

echo [1/4] 检查 OCR 服务 (%OCR_PORT%)...
curl -s http://localhost:%OCR_PORT%/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ OCR服务: 正常
) else (
    echo ❌ OCR服务: 异常或未启动
)

echo [2/4] 检查 Inpaint 服务 (%INPAINT_PORT%)...
curl -s http://localhost:%INPAINT_PORT%/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Inpaint服务: 正常
) else (
    echo ❌ Inpaint服务: 异常或未启动
)

echo [3/4] 检查 API 服务 (%API_PORT%)...
curl -s http://localhost:%API_PORT%/api/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ API服务: 正常
) else (
    echo ❌ API服务: 异常或未启动
)

echo [4/4] 检查前端服务 (%FRONTEND_PORT%)...
curl -s http://localhost:%FRONTEND_PORT% >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 前端服务: 正常
) else (
    echo ❌ 前端服务: 异常或未启动
)

echo.
echo =========================================
echo.
pause
goto menu

:open_urls
cls
echo.
echo 正在打开服务页面...
echo.
start http://localhost:%OCR_PORT%
timeout /t 1 >nul
start http://localhost:%INPAINT_PORT%
timeout /t 1 >nul
start http://localhost:%API_PORT%
timeout /t 1 >nul
start http://localhost:%FRONTEND_PORT%
echo.
echo ✅ 已在浏览器中打开所有服务！
echo.
pause
goto menu

:exit
cls
echo.
echo 感谢使用！再见！
echo.
timeout /t 2 >nul
exit