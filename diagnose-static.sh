#!/bin/bash

echo "🔍 诊断翻译服务静态资源问题"
echo "================================"
echo ""

# 测试直接访问 Docker 服务器
echo "1️⃣ 测试直接访问 Docker 服务器 (47.97.97.198:5001)"
echo "---"
echo "测试根路径:"
curl -I http://47.97.97.198:5001/ 2>&1 | head -5
echo ""

echo "测试静态资源 (直接 /static/ 路径):"
curl -I http://47.97.97.198:5001/static/css/style.css 2>&1 | head -5
echo ""

echo "测试静态资源 (根路径):"
curl -I http://47.97.97.198:5001/static/js/app.js 2>&1 | head -5
echo ""

# 测试通过 nginx
echo "2️⃣ 测试通过 nginx 代理"
echo "---"
echo "测试前端首页:"
curl -I https://offerupup.cn/trans/ 2>&1 | head -5
echo ""

echo "测试静态资源 (CSS):"
curl -I https://offerupup.cn/trans/static/css/style.css 2>&1 | head -5
echo ""

echo "测试静态资源 (JS):"
curl -I https://offerupup.cn/trans/static/js/app.js 2>&1 | head -5
echo ""

# 检查 nginx 日志
echo "3️⃣ 检查 nginx 错误日志 (最近 10 条)"
echo "---"
docker exec nginx tail -10 /var/log/nginx/error.log 2>&1
echo ""

# 检查前端容器
echo "4️⃣ 检查前端容器状态"
echo "---"
echo "容器是否运行:"
ssh root@47.97.97.198 "docker ps | grep translator-frontend" 2>&1
echo ""

echo "前端容器日志 (最近 10 行):"
ssh root@47.97.97.198 "docker logs translator-frontend --tail 10" 2>&1
echo ""

echo "================================"
echo "✅ 诊断完成"
echo ""
echo "💡 常见问题:"
echo "  - 403: 检查前端容器的文件权限或 nginx 配置"
echo "  - 404: 检查路径是否正确"
echo "  - Connection refused: 检查防火墙和端口"
