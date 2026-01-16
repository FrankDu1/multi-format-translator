# 🔧 静态资源 403/404 快速修复指南

## 当前问题
1. 浏览器请求 `/static/` 而不是 `/trans/static/` → **已修复** (更新了 index.html)
2. curl 请求返回 403 → 需要排查后端服务器

---

## ✅ 已完成的修复

### 1. 更新前端 HTML 路径
```html
<!-- 修改前 -->
<link rel="stylesheet" href="/static/css/style.css">
<script src="/static/js/app.js"></script>

<!-- 修改后 -->
<link rel="stylesheet" href="/trans/static/css/style.css">
<script src="/trans/static/js/app.js"></script>
```

### 2. 优化 nginx 静态资源代理
```nginx
location /trans/static/ {
    rewrite ^/trans/static/(.*)$ /static/$1 break;
    proxy_pass http://$translator_frontend_host;
    # 添加了错误处理和缓存控制
}
```

---

## 🚀 立即执行

### 步骤 1: 重新构建前端镜像（HTML 已更新）

```bash
# 在项目根目录
cd translator_frontend

# 构建新镜像
docker build -t translator-frontend:latest .

# 或推送到 GHCR 并在服务器拉取
docker tag translator-frontend:latest ghcr.io/frankdu1/translator-frontend:latest
docker push ghcr.io/frankdu1/translator-frontend:latest

# 在 Docker 服务器 (47.97.97.198) 上
ssh root@47.97.97.198
docker pull ghcr.io/frankdu1/translator-frontend:latest
docker-compose restart translator-frontend
```

### 步骤 2: 更新 nginx 配置

```bash
# 在 nginx 服务器上
# 上传更新后的 nginx-config-update.conf

# 测试配置
docker exec nginx nginx -t

# 重载配置
docker exec nginx nginx -s reload
```

### 步骤 3: 验证修复

```bash
# 运行诊断脚本
chmod +x diagnose-static.sh
./diagnose-static.sh

# 或手动测试
curl -I https://offerupup.cn/trans/static/css/style.css
curl -I https://offerupup.cn/trans/static/js/app.js
```

---

## 🔍 排查 403 错误

### 可能原因 1: 前端容器未正确配置静态文件服务

检查前端容器的 nginx 配置：

```bash
# 进入前端容器
ssh root@47.97.97.198
docker exec -it translator-frontend sh

# 检查文件是否存在
ls -la /app/static/css/
ls -la /app/static/js/

# 检查 nginx 配置
cat /etc/nginx/conf.d/default.conf
```

**如果文件存在但返回 403，可能是权限问题：**
```bash
# 修复权限
docker exec translator-frontend chmod -R 755 /app/static
```

### 可能原因 2: 前端 nginx 未配置 /static/ location

检查 `translator_frontend/nginx.conf`：

```nginx
server {
    listen 5001;
    
    location / {
        root /app;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # ✅ 确保有这个 location
    location /static/ {
        alias /app/static/;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

### 可能原因 3: Docker 容器内文件缺失

检查构建过程：

```dockerfile
# Dockerfile 应该包含
COPY static/ /app/static/
COPY index.html /app/
```

---

## 📋 完整测试命令

```bash
# 1. 测试直接访问 Docker 服务器
curl -I http://47.97.97.198:5001/
curl -I http://47.97.97.198:5001/static/css/style.css
curl -I http://47.97.97.198:5001/static/js/app.js

# 2. 测试通过 nginx
curl -I https://offerupup.cn/trans/
curl -I https://offerupup.cn/trans/static/css/style.css
curl -I https://offerupup.cn/trans/static/js/app.js

# 3. 浏览器测试
# 打开 https://offerupup.cn/trans/
# F12 → Network 标签
# 检查所有资源是否 200 OK
```

---

## 🎯 预期结果

**所有请求应返回：**
```
HTTP/2 200 
server: nginx
content-type: text/css   # 或 application/javascript
cache-control: public, immutable
expires: ...
```

---

## ⚠️ 临时解决方案（如果重建镜像需要时间）

在前端容器内直接修改文件：

```bash
# 进入容器
docker exec -it translator-frontend sh

# 备份原文件
cp /app/index.html /app/index.html.bak

# 使用 sed 修改路径
sed -i 's|href="/static/|href="/trans/static/|g' /app/index.html
sed -i 's|src="/static/|src="/trans/static/|g' /app/index.html

# 重启 nginx
nginx -s reload

# 退出容器
exit
```

**注意：这是临时方案，容器重启后会丢失！**

---

## 📞 仍然有问题？

运行诊断脚本并提供输出：
```bash
./diagnose-static.sh > debug.log 2>&1
cat debug.log
```

检查以下信息：
1. 前端容器是否正常运行
2. 直接访问 47.97.97.198:5001 是否正常
3. nginx 错误日志中的详细信息
4. 前端容器内 /app/static/ 目录是否存在
