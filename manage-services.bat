@echo off
REM 🔥 设置 UTF-8 编码
chcp 65001 >nul

REM 🔥 加载环境变量
if exist .env (
    for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
        if not "%%a"=="" if not "%%a:~0,1"=="#" set "%%a=%%b"
    )
)

REM 🔥 设置默认值
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
echo   当前工作目录: %SCRIPT_DIR%
echo.
echo   1. 启动所有服务
echo   2. 停止所有服务
echo   3. 停止单个服务
echo   4. 重启所有服务 / 单个服务
echo   5. 查看服务状态
echo   6. 查看日志文件
echo   7. 健康检查
echo   8. 清理日志文件
echo   9. 打开服务URL
echo   0. 退出
echo.
echo =========================================
echo.

set /p choice=请选择操作 (0-9): 

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto stop_single
if "%choice%"=="4" goto restart
if "%choice%"=="5" goto status
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto health
if "%choice%"=="8" goto clean
if "%choice%"=="9" goto open_urls
if "%choice%"=="0" goto exit
goto menu

:start
cls
echo.
echo 正在启动所有服务 (后台模式)...
echo.
cd /d "%SCRIPT_DIR%"
if not exist "logs" mkdir logs

REM 🔥 OCR 服务 (后台 + UTF-8)
echo [1/4] 启动 OCR 服务 (%OCR_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && set OCR_PORT=%OCR_PORT% && cd /d "%SCRIPT_DIR%\ocr" && python app.py > "%SCRIPT_DIR%\logs\ocr.log" 2>&1"
timeout /t 2 >nul

REM 🔥 Inpaint 服务 (后台 + UTF-8)
echo [2/4] 启动 Inpaint 服务 (%INPAINT_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && set INPAINT_PORT=%INPAINT_PORT% && cd /d "%SCRIPT_DIR%\inpaint" && python app.py > "%SCRIPT_DIR%\logs\inpaint.log" 2>&1"
timeout /t 2 >nul

REM 🔥 API 服务 (后台 + UTF-8)
echo [3/4] 启动 API 服务 (%API_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && set API_PORT=%API_PORT% && cd /d "%SCRIPT_DIR%\translator_api" && python app.py > "%SCRIPT_DIR%\logs\api.log" 2>&1"
timeout /t 2 >nul

REM 🔥 前端服务 (后台 + UTF-8)
echo [4/4] 启动前端服务 (%FRONTEND_PORT%)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && cd /d "%SCRIPT_DIR%\translator_frontend" && python -m http.server %FRONTEND_PORT% > "%SCRIPT_DIR%\logs\frontend.log" 2>&1"

echo.
echo =========================================
echo ✅ 所有服务已在后台启动！
echo =========================================
echo.
echo 服务地址:
echo   OCR:      http://localhost:%OCR_PORT%
echo   Inpaint:  http://localhost:%INPAINT_PORT%
echo   API:      http://localhost:%API_PORT%
echo   前端:     http://localhost:%FRONTEND_PORT%
echo.
echo 日志文件:
echo   logs/ocr.log
echo   logs/inpaint.log
echo   logs/api.log
echo   logs/frontend.log
echo.
echo 💡 提示: 已启用 UTF-8 支持和代理绕过
echo.
pause
goto menu

:stop
cls
echo.
echo 正在停止所有服务...
echo.

REM 停止占用端口的进程
echo [1/4] 停止 OCR 服务 (%OCR_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%OCR_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo [2/4] 停止 Inpaint 服务 (%INPAINT_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%INPAINT_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo [3/4] 停止 API 服务 (%API_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%API_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo [4/4] 停止前端服务 (%FRONTEND_PORT%)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo.
echo ✅ 所有服务已停止！
echo.
pause
goto menu

:stop_single
cls
echo =========================================
echo         选择要停止的服务
echo =========================================
echo.
echo   1. OCR 服务 (%OCR_PORT%)
echo   2. Inpaint 服务 (%INPAINT_PORT%)
echo   3. API 服务 (%API_PORT%)
echo   4. 前端服务 (%FRONTEND_PORT%)
echo   0. 返回主菜单
echo.
echo =========================================
echo.

set /p stop_choice=请选择要停止的服务 (0-4): 

if "%stop_choice%"=="0" goto menu
if "%stop_choice%"=="1" goto stop_ocr
if "%stop_choice%"=="2" goto stop_inpaint
if "%stop_choice%"=="3" goto stop_api
if "%stop_choice%"=="4" goto stop_frontend

echo.
echo ❌ 无效选择！
timeout /t 2 >nul
goto stop_single

:stop_ocr
echo.
echo 正在停止 OCR 服务 (29001)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
echo ✅ OCR 服务已停止！
echo.
pause
goto menu

:stop_inpaint
echo.
echo 正在停止 Inpaint 服务 (29002)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29002" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
echo ✅ Inpaint 服务已停止！
echo.
pause
goto menu

:stop_api
echo.
echo 正在停止 API 服务 (29003)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29003" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
echo ✅ API 服务已停止！
echo.
pause
goto menu

:stop_frontend
echo.
echo 正在停止前端服务 (5001)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
echo ✅ 前端服务已停止！
echo.
pause
goto menu

:restart
cls
echo =========================================
echo         重启服务菜单
echo =========================================
echo.
echo   1. 重启所有服务
echo   2. 重启单个服务
echo   0. 返回主菜单
echo.
echo =========================================
echo.

set /p restart_choice=请选择操作 (0-2): 

if "%restart_choice%"=="1" goto restart_all
if "%restart_choice%"=="2" goto restart_single
if "%restart_choice%"=="0" goto menu
goto restart

:restart_all
cls
echo.
echo 正在重启所有服务...
echo.

REM 停止所有服务
echo 停止所有服务...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29002" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29003" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

echo.
echo 等待 3 秒...
timeout /t 3 >nul

REM 启动所有服务
cd /d "%SCRIPT_DIR%"
if not exist "logs" mkdir logs

echo.
echo 启动所有服务...
echo [1/4] 启动 OCR 服务 (29001)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && cd /d "%SCRIPT_DIR%\ocr" && python app.py > "%SCRIPT_DIR%\logs\ocr.log" 2>&1"
timeout /t 2 >nul

echo [2/4] 启动 Inpaint 服务 (29002)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && cd /d "%SCRIPT_DIR%\inpaint" && python app.py > "%SCRIPT_DIR%\logs\inpaint.log" 2>&1"
timeout /t 2 >nul

echo [3/4] 启动 API 服务 (29003)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && cd /d "%SCRIPT_DIR%\translator_api" && python app.py > "%SCRIPT_DIR%\logs\api.log" 2>&1"
timeout /t 2 >nul

echo [4/4] 启动前端服务 (5001)...
start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && cd /d "%SCRIPT_DIR%\translator_frontend" && python -m http.server 5001 > "%SCRIPT_DIR%\logs\frontend.log" 2>&1"

echo.
echo ✅ 所有服务已重启完成！
echo.
pause
goto menu

:restart_single
cls
echo =========================================
echo         选择要重启的服务
echo =========================================
echo.
echo   1. OCR 服务 (29001)
echo   2. Inpaint 服务 (29002)
echo   3. API 服务 (29003)
echo   4. 前端服务 (5001)
echo   0. 返回重启菜单
echo.
echo =========================================
echo.

set /p single_choice=请选择要重启的服务 (0-4): 

if "%single_choice%"=="0" goto restart

cd /d "%SCRIPT_DIR%"
if not exist "logs" mkdir logs

REM 重启 OCR 服务
if "%single_choice%"=="1" (
    echo.
    echo 正在停止 OCR 服务...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
    echo 等待 2 秒...
    timeout /t 2 >nul
    echo 正在启动 OCR 服务...
    start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && cd /d "%SCRIPT_DIR%\ocr" && python app.py > "%SCRIPT_DIR%\logs\ocr.log" 2>&1"
)

REM 重启 Inpaint 服务
if "%single_choice%"=="2" (
    echo.
    echo 正在停止 Inpaint 服务...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29002" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
    echo 等待 2 秒...
    timeout /t 2 >nul
    echo 正在启动 Inpaint 服务...
    start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && cd /d "%SCRIPT_DIR%\inpaint" && python app.py > "%SCRIPT_DIR%\logs\inpaint.log" 2>&1"
)

REM 重启 API 服务
if "%single_choice%"=="3" (
    echo.
    echo 正在停止 API 服务...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":29003" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
    echo 等待 2 秒...
    timeout /t 2 >nul
    echo 正在启动 API 服务...
    start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && set NO_PROXY=localhost,127.0.0.1 && cd /d "%SCRIPT_DIR%\translator_api" && python app.py > "%SCRIPT_DIR%\logs\api.log" 2>&1"
)

REM 重启前端服务
if "%single_choice%"=="4" (
    echo.
    echo 正在停止前端服务...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5001" ^| findstr "LISTENING"') do taskkill /PID %%a /F >nul 2>&1
    echo 等待 2 秒...
    timeout /t 2 >nul
    echo 正在启动前端服务...
    start /B "" cmd /c "chcp 65001 >nul && set PYTHONIOENCODING=utf-8 && cd /d "%SCRIPT_DIR%\translator_frontend" && python -m http.server 5001 > "%SCRIPT_DIR%\logs\frontend.log" 2>&1"
)

if "%single_choice%"=="1" goto single_restart_complete
if "%single_choice%"=="2" goto single_restart_complete
if "%single_choice%"=="3" goto single_restart_complete
if "%single_choice%"=="4" goto single_restart_complete

echo.
echo ❌ 无效选择！
timeout /t 2 >nul
goto restart_single

:single_restart_complete
echo.
echo ✅ 服务重启完成！
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

netstat -ano | findstr ":29001.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ OCR服务 ^(29001^): 运行中
) else (
    echo ❌ OCR服务 ^(29001^): 未运行
)

netstat -ano | findstr ":29002.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Inpaint服务 ^(29002^): 运行中
) else (
    echo ❌ Inpaint服务 ^(29002^): 未运行
)

netstat -ano | findstr ":29003.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ API服务 ^(29003^): 运行中
) else (
    echo ❌ API服务 ^(29003^): 未运行
)

netstat -ano | findstr ":5001.*LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ 前端服务 ^(5001^): 运行中
) else (
    echo ❌ 前端服务 ^(5001^): 未运行
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

echo [1/4] 检查 OCR 服务 (29001)...
curl -s http://localhost:29001/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ OCR服务: 正常
) else (
    echo ❌ OCR服务: 异常或未启动
)

echo [2/4] 检查 Inpaint 服务 (29002)...
curl -s http://localhost:29002/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ Inpaint服务: 正常
) else (
    echo ❌ Inpaint服务: 异常或未启动
)

echo [3/4] 检查 API 服务 (29003)...
curl -s http://localhost:29003/api/health >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo ✅ API服务: 正常
) else (
    echo ❌ API服务: 异常或未启动
)

echo [4/4] 检查前端服务 (5001)...
curl -s http://localhost:5001 >nul 2>&1
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

:clean
cls
echo.
echo ⚠️  警告: 这将删除所有日志文件！
echo.
set /p confirm=确认继续? (y/n): 

if /i "%confirm%"=="y" (
    if exist "%SCRIPT_DIR%\logs" (
        del /Q "%SCRIPT_DIR%\logs\*.log" 2>nul
        echo.
        echo ✅ 日志文件已清理！
    ) else (
        echo.
        echo ⚠️  日志目录不存在
    )
) else (
    echo.
    echo 已取消操作
)
echo.
pause
goto menu

:open_urls
cls
echo.
echo 正在打开服务页面...
echo.
start http://localhost:29001
timeout /t 1 >nul
start http://localhost:29002
timeout /t 1 >nul
start http://localhost:29003
timeout /t 1 >nul
start http://localhost:5001
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