FROM docker.1ms.run/nginx:alpine

LABEL maintainer="translator@example.com"
LABEL description="Image Translator Frontend - Static Web App with .env support"

# 安装必要的工具
RUN apk add --no-cache bash dos2unix

# 复制前端文件到 Nginx 根目录
COPY index.html /usr/share/nginx/html/index.html
COPY static /usr/share/nginx/html/static

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 复制环境变量注入脚本并转换换行符
COPY docker-entrypoint.sh /docker-entrypoint.d/40-inject-env.sh
RUN dos2unix /docker-entrypoint.d/40-inject-env.sh && \
    chmod +x /docker-entrypoint.d/40-inject-env.sh

EXPOSE 5001

# Nginx 会自动执行 /docker-entrypoint.d/ 中的脚本
CMD ["nginx", "-g", "daemon off;"]
