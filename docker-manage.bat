@echo off
chcp 65001 >nul
title Docker部署管理 - 多格式翻译工具
color 0A

:menu
cls
echo.
echo ========================================
echo    Docker部署管理 - 翻译服务
echo ========================================
echo.
echo 当前状态:
docker-compose ps 2>nul
echo.
echo ========================================
echo    请选择操作:
echo ========================================
echo.
echo [1] 🚀 一键启动所有服务（构建+运行）
echo [2] 📦 仅构建镜像（不启动）
echo [3] ▶️  启动已构建的服务
echo [4] ⏸️  停止所有服务
echo [5] 🔄 重启所有服务
echo [6] 📊 查看服务状态
echo [7] 📝 查看实时日志
echo [8] 🧹 清理停止的服务
echo [9] 🗑️  完全清理（包括数据卷）
echo [10] 🔧 重新构建并启动
echo [0] ❌ 退出
echo.
echo ========================================
set /p choice=请输入选项 (0-10): 

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto build_only
if "%choice%"=="3" goto start_only
if "%choice%"=="4" goto stop
if "%choice%"=="5" goto restart
if "%choice%"=="6" goto status
if "%choice%"=="7" goto logs
if "%choice%"=="8" goto clean
if "%choice%"=="9" goto clean_all
if "%choice%"=="10" goto rebuild
if "%choice%"=="0" goto end

echo 无效选项，请重新选择
timeout /t 2 >nul
goto menu

:start_all
cls
echo ========================================
echo    🚀 一键启动所有服务
echo ========================================
echo.
echo 正在检查Docker环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到Docker，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/get-started
    pause
    goto menu
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到docker-compose
    pause
    goto menu
)

echo ✅ Docker环境正常
echo.
echo 正在检查配置文件...
if not exist ".env" (
    echo ⚠️  未找到 .env 文件，使用默认配置
    if exist ".env.example" (
        echo 创建 .env 文件...
        copy .env.example .env >nul
        echo ✅ 已从 .env.example 创建 .env
    )
) else (
    echo ✅ 配置文件存在
)
echo.
echo ========================================
echo 开始构建并启动服务...
echo 第一次运行可能需要10-15分钟下载依赖
echo ========================================
echo.
docker-compose up -d --build

if errorlevel 1 (
    echo.
    echo ❌ 启动失败！请检查错误信息
    pause
    goto menu
)

echo.
echo ========================================
echo ✅ 所有服务启动成功！
echo ========================================
echo.
echo 服务地址:
echo   前端界面: http://localhost:5001
echo   API服务:  http://localhost:5002
echo   OCR服务:  http://localhost:8899
echo   Inpaint:  http://localhost:8900
echo.
echo 提示: 等待1-2分钟让服务完全启动
echo.
pause
goto menu

:build_only
cls
echo ========================================
echo    📦 构建Docker镜像
echo ========================================
echo.
docker-compose build
echo.
if errorlevel 1 (
    echo ❌ 构建失败！
) else (
    echo ✅ 构建成功！
)
pause
goto menu

:start_only
cls
echo ========================================
echo    ▶️  启动服务
echo ========================================
echo.
docker-compose up -d
echo.
if errorlevel 1 (
    echo ❌ 启动失败！
) else (
    echo ✅ 启动成功！
    echo.
    echo 访问地址: http://localhost:5001
)
pause
goto menu

:stop
cls
echo ========================================
echo    ⏸️  停止所有服务
echo ========================================
echo.
docker-compose down
echo.
echo ✅ 所有服务已停止
pause
goto menu

:restart
cls
echo ========================================
echo    🔄 重启所有服务
echo ========================================
echo.
docker-compose restart
echo.
echo ✅ 所有服务已重启
pause
goto menu

:status
cls
echo ========================================
echo    📊 服务状态
echo ========================================
echo.
docker-compose ps
echo.
echo ========================================
echo    容器资源使用情况
echo ========================================
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" translator-frontend translator-api translator-ocr translator-inpaint 2>nul
echo.
pause
goto menu

:logs
cls
echo ========================================
echo    📝 实时日志
echo ========================================
echo.
echo 按 Ctrl+C 退出日志查看
echo.
timeout /t 2 >nul
docker-compose logs -f --tail=100
goto menu

:clean
cls
echo ========================================
echo    🧹 清理停止的容器
echo ========================================
echo.
docker-compose down
echo.
echo ✅ 清理完成
pause
goto menu

:clean_all
cls
echo ========================================
echo    🗑️  完全清理
echo ========================================
echo.
echo ⚠️  警告: 这将删除所有容器、镜像和数据卷
echo 确定要继续吗？(Y/N)
set /p confirm=
if /i not "%confirm%"=="Y" goto menu

echo.
echo 正在清理...
docker-compose down -v
docker system prune -f
echo.
echo ✅ 清理完成
pause
goto menu

:rebuild
cls
echo ========================================
echo    🔧 重新构建并启动
echo ========================================
echo.
echo 停止现有服务...
docker-compose down
echo.
echo 重新构建镜像...
docker-compose build --no-cache
echo.
echo 启动服务...
docker-compose up -d
echo.
if errorlevel 1 (
    echo ❌ 重建失败！
) else (
    echo ✅ 重建成功！
    echo.
    echo 访问地址: http://localhost:5001
)
pause
goto menu

:end
cls
echo.
echo 感谢使用！
echo.
timeout /t 1 >nul
exit
