#!/bin/bash

# 🔄 Docker Nginx 配置重载脚本

echo "🔄 重载 Docker Nginx 配置..."

# 方法 1: 热重载（推荐，不中断服务）
echo "1️⃣ 测试配置..."
docker exec nginx nginx -t

if [ $? -eq 0 ]; then
    echo "✅ 配置测试通过"
    echo "2️⃣ 重载配置..."
    docker exec nginx nginx -s reload
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx 配置已重载！"
        echo ""
        echo "📊 Nginx 状态："
        docker exec nginx nginx -V 2>&1 | head -1
    else
        echo "❌ 重载失败！"
    fi
else
    echo "❌ 配置测试失败，未执行重载"
    echo ""
    echo "📋 查看详细错误："
    echo "docker exec nginx nginx -t"
fi

echo ""
echo "💡 其他有用命令："
echo "  查看日志: docker logs -f nginx"
echo "  重启容器: docker restart nginx"
echo "  进入容器: docker exec -it nginx bash"
