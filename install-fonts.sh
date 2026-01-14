#!/bin/bash

# 🎨 Ubuntu 服务器中文字体安装脚本
# 适用于 Ubuntu 18.04+, Debian 10+

set -e

echo "======================================"
echo "🎨 安装中文字体"
echo "======================================"

# 1. 更新软件包列表
echo ""
echo "📦 更新软件包列表..."
sudo apt-get update -y

# 2. 安装常用中文字体包
echo ""
echo "🔤 安装字体包..."
sudo apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-arphic-ukai \
    fonts-arphic-uming \
    xfonts-wqy

# 3. 刷新字体缓存
echo ""
echo "♻️  刷新字体缓存..."
sudo fc-cache -fv

# 4. 验证字体安装
echo ""
echo "✅ 验证字体安装..."
fc-list :lang=zh | head -n 5

echo ""
echo "======================================"
echo "✅ 字体安装完成！"
echo "======================================"
echo ""
echo "已安装的字体包括："
echo "  • Noto Sans CJK (Google 开源字体)"
echo "  • WenQuanYi Zen Hei (文泉驿正黑)"
echo "  • WenQuanYi Micro Hei (文泉驿微米黑)"
echo "  • AR PL UKai (文鼎 PL 简报宋)"
echo ""
echo "重启 Docker 容器以应用更改："
echo "  docker-compose restart translator-api"
echo ""
