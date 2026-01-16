# 🌐 Nginx 配置部署指南

## 📋 配置说明

### 服务路径映射

```
https://offerupup.top/trans              → 翻译前端 (translator-frontend:5001)
https://offerupup.top/translator-api/    → 翻译 API (translator-api:5002)
https://offerupup.top/openchatbox/       → OpenChatBox (openchatbox:8000)
https://offerupup.top/                   → WordPress 主站 (wordpress:80)
```

### CORS 配置

已在 `/translator-api/` 路径添加完整的 CORS 支持：
- ✅ 允许所有域名访问（`Access-Control-Allow-Origin: *`）
- ✅ 支持 OPTIONS 预检请求
- ✅ 允许常用 HTTP 方法
- ✅ 允许自定义请求头
- ✅ 响应头自动添加 CORS 头

---

## 🚀 部署步骤

### 1. 备份现有配置

```bash
# 备份当前 nginx 配置
sudo cp /etc/nginx/sites-available/offerupup.top /etc/nginx/sites-available/offerupup.top.backup.$(date +%Y%m%d)

# 或者如果在 conf.d 目录
sudo cp /etc/nginx/conf.d/offerupup.top.conf /etc/nginx/conf.d/offerupup.top.conf.backup.$(date +%Y%m%d)
```

### 2. 上传新配置

```bash
# 方法 A：直接编辑服务器配置文件
sudo nano /etc/nginx/sites-available/offerupup.top

# 方法 B：上传配置文件
scp nginx-config-update.conf user@server:/tmp/
sudo mv /tmp/nginx-config-update.conf /etc/nginx/sites-available/offerupup.top
```

### 3. 测试配置

```bash
# 测试 nginx 配置语法
sudo nginx -t

# 应该看到：
# nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
# nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### 4. 重载 Nginx

```bash
# 热重载配置（不中断服务）
sudo nginx -s reload

# 或者重启 nginx 服务
sudo systemctl reload nginx
```

### 5. 更新前端配置

前端的 `ENV_CONFIG` 会自动检测域名并使用正确的 API 路径：

```javascript
// 生产环境（域名访问）
API_BASE_URL = '/translator-api/api'

// 访问路径示例：
https://offerupup.top/translator-api/api/translate/image
https://offerupup.top/translator-api/api/translate/pdf
```

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
# 检查 nginx 状态
sudo systemctl status nginx

# 检查 Docker 容器
docker ps | grep translator

# 应该看到：
# translator-frontend
# translator-api
```

### 2. 测试前端访问

```bash
# 测试前端页面
curl -I https://offerupup.top/trans

# 应该返回 200 OK
```

### 3. 测试 API 访问

```bash
# 测试 API 健康检查（如果有）
curl https://offerupup.top/translator-api/api/health

# 测试 CORS 预检
curl -X OPTIONS https://offerupup.top/translator-api/api/translate/image \
  -H "Origin: https://offerupup.top" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# 应该看到 CORS 响应头：
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: GET, POST, OPTIONS, PUT, DELETE
```

### 4. 浏览器测试

1. 访问：`https://offerupup.top/trans`
2. 上传图片进行翻译
3. 打开浏览器开发者工具（F12）→ Network 标签
4. 检查 API 请求是否成功，无 CORS 错误

---

## 🔧 常见问题

### Q1: 404 Not Found
**原因：** Docker 容器名称不匹配

**解决：**
```bash
# 检查实际容器名称
docker ps --format "table {{.Names}}\t{{.Ports}}"

# 修改 nginx 配置中的容器名称
# translator-frontend:5001 → 实际容器名
# translator-api:5002 → 实际容器名
```

### Q2: 502 Bad Gateway
**原因：** 容器未启动或网络不通

**解决：**
```bash
# 1. 检查容器状态
docker ps -a | grep translator

# 2. 启动容器
docker-compose up -d translator-frontend translator-api

# 3. 检查容器日志
docker logs translator-frontend
docker logs translator-api

# 4. 确认网络连接
docker network ls
docker network inspect bridge  # 或你使用的网络名称
```

### Q3: CORS 错误仍然存在
**原因：** CORS 头未正确传递或被覆盖

**解决：**
```bash
# 1. 检查 nginx 错误日志
sudo tail -f /var/log/nginx/error.log

# 2. 确认 CORS 头在响应中
curl -I https://offerupup.top/translator-api/api/translate/image

# 3. 如果仍有问题，在后端 Flask app.py 中设置 CORS
# (已在之前配置中完成)
```

### Q4: 文件上传失败
**原因：** 文件大小超过限制

**解决：**
```nginx
# 在 nginx 配置中增加上传限制
location /translator-api/ {
    client_max_body_size 100M;  # 已添加
}
```

同时检查 Flask 配置：
```python
# app.py
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

### Q5: 翻译超时
**原因：** 处理时间过长，nginx 超时

**解决：**
```nginx
# 已在配置中设置为 300 秒（5分钟）
proxy_connect_timeout 300;
proxy_send_timeout 300;
proxy_read_timeout 300;
```

---

## 📊 性能优化

### 1. 启用 Gzip 压缩

在 nginx 主配置添加：
```nginx
# /etc/nginx/nginx.conf
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
```

### 2. 静态资源缓存

已在配置中添加：
```nginx
location /trans/static/ {
    expires 7d;
    add_header Cache-Control "public, immutable";
}
```

### 3. 连接池优化

```nginx
# 在 upstream 块中配置（可选）
upstream translator_api {
    server translator-api:5002 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

location /translator-api/ {
    proxy_pass http://translator_api/;
}
```

---

## 📝 配置清单

部署前确认：

- [ ] 备份现有 nginx 配置
- [ ] 修改容器名称（如果不同）
- [ ] 测试 nginx 配置语法
- [ ] 确认 Docker 容器运行中
- [ ] 重载 nginx 配置
- [ ] 测试前端访问
- [ ] 测试 API 访问
- [ ] 验证 CORS 正常工作
- [ ] 测试文件上传（图片、PDF、PPT）
- [ ] 检查 nginx 日志无错误

---

## 🔗 相关文件

- Nginx 配置：`nginx-config-update.conf`
- 前端配置：`translator_frontend/index.html` (ENV_CONFIG)
- 后端配置：`translator_api/config.py` (CORS settings)
- Docker 配置：`docker-compose.yml`

---

## 📞 故障排查命令

```bash
# 实时查看 nginx 日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 查看容器日志
docker logs -f translator-frontend
docker logs -f translator-api

# 测试 DNS 解析
nslookup translator-frontend
nslookup translator-api

# 测试容器网络连接
docker exec -it nginx curl http://translator-frontend:5001
docker exec -it nginx curl http://translator-api:5002/api/health

# 重启服务
sudo systemctl restart nginx
docker-compose restart translator-frontend translator-api
```

---

## 🎯 访问地址

部署成功后，访问地址：

**前端页面：**
```
https://offerupup.top/trans
```

**API 端点：**
```
https://offerupup.top/translator-api/api/translate/image
https://offerupup.top/translator-api/api/translate/pdf
https://offerupup.top/translator-api/api/translate/ppt
https://offerupup.top/translator-api/api/translate/text
```

**测试 CORS：**
```bash
curl -X OPTIONS https://offerupup.top/translator-api/api/translate/image \
  -H "Origin: https://offerupup.top" \
  -H "Access-Control-Request-Method: POST" \
  -i
```
