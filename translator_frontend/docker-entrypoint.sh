#!/bin/sh
# 环境变量注入脚本
# 用于在容器启动时设置正确的环境配置

# 默认环境为 production
APP_ENV=${APP_ENV:-production}

echo "Setting APP_ENV to: $APP_ENV"

# 替换 index.html 中的环境配置
sed -i "s/<meta name=\"app-env\" content=\"[^\"]*\">/<meta name=\"app-env\" content=\"$APP_ENV\">/" /usr/share/nginx/html/index.html

echo "Environment configuration updated successfully"

# 启动 nginx
exec nginx -g "daemon off;"
