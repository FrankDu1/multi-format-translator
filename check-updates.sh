#!/bin/bash
# 检查并更新 Docker 镜像

echo "🔍 检查镜像更新..."

services=("translator-frontend" "translator-api" "translator-ocr" "translator-inpaint")

for service in "${services[@]}"; do
    echo ""
    echo "📦 检查 $service..."
    
    # 获取本地镜像 ID
    local_id=$(docker images ghcr.io/frankdu1/$service:main --format "{{.ID}}" 2>/dev/null)
    
    # 拉取最新镜像（不实际下载，只检查）
    docker pull ghcr.io/frankdu1/$service:main > /dev/null 2>&1
    
    # 获取远程镜像 ID
    remote_id=$(docker images ghcr.io/frankdu1/$service:main --format "{{.ID}}" | head -n1)
    
    if [ "$local_id" != "$remote_id" ]; then
        echo "  ⚠️  有新版本可用"
        echo "     本地: $local_id"
        echo "     远程: $remote_id"
    else
        echo "  ✅ 已是最新版本"
    fi
done

echo ""
echo "💡 要更新所有服务，请运行："
echo "   docker compose -f docker-compose.ghcr.yml pull"
echo "   docker compose -f docker-compose.ghcr.yml up -d"
