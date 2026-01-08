#!/bin/bash
# 服务器部署脚本 - 在服务器上运行

set -e

echo "🔄 更新 Docker 镜像..."
docker compose -f docker-compose.ghcr.yml pull

echo "🚀 重启服务..."
docker compose -f docker-compose.ghcr.yml up -d

echo "📊 查看服务状态..."
docker compose -f docker-compose.ghcr.yml ps

echo "✅ 部署完成！"
