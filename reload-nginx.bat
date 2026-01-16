@echo off
REM Docker Nginx 配置重载脚本 (Windows)

echo 🔄 重载 Docker Nginx 配置...
echo.

REM 测试配置
echo 1️⃣ 测试配置...
docker exec nginx nginx -t

if %errorlevel% equ 0 (
    echo ✅ 配置测试通过
    echo.
    echo 2️⃣ 重载配置...
    docker exec nginx nginx -s reload
    
    if %errorlevel% equ 0 (
        echo ✅ Nginx 配置已重载！
        echo.
        echo 📊 Nginx 状态：
        docker exec nginx nginx -V 2>&1 | findstr "nginx version"
    ) else (
        echo ❌ 重载失败！
    )
) else (
    echo ❌ 配置测试失败，未执行重载
    echo.
    echo 📋 查看详细错误：
    echo docker exec nginx nginx -t
)

echo.
echo 💡 其他有用命令：
echo   查看日志: docker logs -f nginx
echo   重启容器: docker restart nginx
echo   进入容器: docker exec -it nginx bash
echo.

pause
