#!/bin/bash
# 使用 latest 标签快速部署脚本

set -e

echo "========================================="
echo "🚀 多格式翻译服务 - 快速部署"
echo "========================================="

echo -e "\n1️⃣  停止旧服务..."
docker-compose -f docker-compose.ghcr.latest.yml down

echo -e "\n2️⃣  拉取最新镜像（使用 latest 标签）..."
docker-compose -f docker-compose.ghcr.latest.yml pull

echo -e "\n3️⃣  启动服务..."
docker-compose -f docker-compose.ghcr.latest.yml up -d

echo -e "\n4️⃣  等待服务启动..."
sleep 10

echo -e "\n5️⃣  检查服务状态..."
docker-compose -f docker-compose.ghcr.latest.yml ps

echo -e "\n6️⃣  查看日志..."
docker-compose -f docker-compose.ghcr.latest.yml logs --tail=20

echo -e "\n========================================="
echo "✅ 部署完成！"
echo "========================================="
echo ""
echo "服务地址："
echo "  前端: http://localhost:5001"
echo "  API:  http://localhost:5002"
echo "  OCR:  http://localhost:8899"
echo ""
echo "查看日志: docker-compose -f docker-compose.ghcr.latest.yml logs -f"
echo "停止服务: docker-compose -f docker-compose.ghcr.latest.yml down"
echo ""
