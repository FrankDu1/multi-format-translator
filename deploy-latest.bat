@echo off
REM 使用 latest 标签快速部署脚本 (Windows)

echo =========================================
echo 🚀 多格式翻译服务 - 快速部署
echo =========================================

echo.
echo 1️⃣  停止旧服务...
docker-compose -f docker-compose.ghcr.latest.yml down

echo.
echo 2️⃣  拉取最新镜像（使用 latest 标签）...
docker-compose -f docker-compose.ghcr.latest.yml pull

echo.
echo 3️⃣  启动服务...
docker-compose -f docker-compose.ghcr.latest.yml up -d

echo.
echo 4️⃣  等待服务启动...
timeout /t 10 /nobreak > nul

echo.
echo 5️⃣  检查服务状态...
docker-compose -f docker-compose.ghcr.latest.yml ps

echo.
echo =========================================
echo ✅ 部署完成！
echo =========================================
echo.
echo 服务地址：
echo   前端: http://localhost:5001
echo   API:  http://localhost:5002
echo   OCR:  http://localhost:8899
echo.
echo 查看日志: docker-compose -f docker-compose.ghcr.latest.yml logs -f
echo 停止服务: docker-compose -f docker-compose.ghcr.latest.yml down
echo.
