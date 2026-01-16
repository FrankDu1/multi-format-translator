# 🔧 404 错误调试指南

## 问题现象
```
Failed to load resource: the server responded with a status of 404
```

## 🎯 已修复的问题

### 1. 路径重写规则
**修改前：**
```nginx
location /trans {
    proxy_pass http://$translator_frontend_host;
}
```

**修改后：**
```nginx
# 自动添加尾部斜杠
location = /trans {
    return 301 $scheme://$host/trans/;
}

# 去掉 /trans 前缀，传递根路径给容器
location /trans/ {
    rewrite ^/trans/(.*)$ /$1 break;
    proxy_pass http://$translator_frontend_host;
}
```

### 2. 静态资源路径
**修改前：**
```nginx
location /trans/static/ {
    proxy_pass http://$translator_frontend_host/static/;
}
```

**修改后：**
```nginx
location /trans/static/ {
    rewrite ^/trans/(.*)$ /$1 break;
    proxy_pass http://$translator_frontend_host;
}
```

---

## ✅ 测试步骤

### 1. 更新 Nginx 配置

```bash
# 1. 上传新配置
scp nginx-config-update.conf user@nginx-server:/tmp/

# 2. SSH 到服务器
ssh user@nginx-server

# 3. 备份原配置
sudo cp /etc/nginx/sites-available/offerupup.top /etc/nginx/sites-available/offerupup.top.bak

# 4. 应用新配置
sudo cp /tmp/nginx-config-update.conf /etc/nginx/sites-available/offerupup.top

# 5. 测试配置
sudo nginx -t

# 6. 重载配置
sudo nginx -s reload
```

### 2. 验证路径映射

```bash
# 测试前端首页（应该自动重定向到 /trans/）
curl -I https://offerupup.top/trans

# 预期结果：
# HTTP/1.1 301 Moved Permanently
# Location: https://offerupup.top/trans/

# 测试前端首页（带斜杠）
curl -I https://offerupup.top/trans/

# 预期结果：
# HTTP/1.1 200 OK

# 测试静态资源
curl -I https://offerupup.top/trans/static/css/style.css

# 预期结果：
# HTTP/1.1 200 OK

# 测试 API
curl -I https://offerupup.top/translator-api/api/health

# 预期结果：
# HTTP/1.1 200 OK 或 404 (如果没有 health endpoint)
```

### 3. 浏览器测试

1. 清除浏览器缓存（Ctrl+Shift+Delete）
2. 访问 `https://offerupup.top/trans`
3. 打开开发者工具（F12）→ Network 标签
4. 刷新页面（Ctrl+F5）
5. 检查所有资源是否正常加载（状态码 200）

---

## 🔍 常见 404 错误及解决方案

### 错误 1: `/trans` 返回 404
**原因：** 缺少尾部斜杠

**解决：** 已添加自动重定向
```nginx
location = /trans {
    return 301 $scheme://$host/trans/;
}
```

### 错误 2: `/trans/static/css/style.css` 返回 404
**原因：** 路径前缀未去除

**解决：** 使用 rewrite 去除前缀
```nginx
location /trans/static/ {
    rewrite ^/trans/(.*)$ /$1 break;
    proxy_pass http://$translator_frontend_host;
}
```

### 错误 3: API 请求返回 404
**原因：** API 路径配置错误

**检查：**
```bash
# 直接访问 Docker 服务器
curl http://40.162.204.61:5002/api/translate/image

# 通过 nginx 访问
curl https://offerupup.top/translator-api/api/translate/image
```

**修复：** 确认 API 实际路径
```nginx
# 如果后端 API 路径是 /api/xxx
location /translator-api/ {
    proxy_pass http://$translator_api_host/;  # 注意尾部斜杠
}

# 如果后端 API 路径是 /xxx（没有 /api 前缀）
location /translator-api/api/ {
    rewrite ^/translator-api/api/(.*)$ /api/$1 break;
    proxy_pass http://$translator_api_host;
}
```

### 错误 4: 下载文件返回 404
**原因：** 文件路径配置问题

**检查前端代码：**
```javascript
// 确认 ENV_CONFIG 配置正确
console.log('API_BASE_URL:', ENV_CONFIG.API_BASE_URL);

// 应该输出：
// /translator-api/api
```

---

## 📊 调试命令

### 查看 Nginx 日志

```bash
# 实时查看访问日志
sudo tail -f /var/log/nginx/access.log

# 实时查看错误日志
sudo tail -f /var/log/nginx/error.log

# 过滤 404 错误
sudo grep "404" /var/log/nginx/access.log | tail -20

# 查看特定路径的请求
sudo grep "/trans" /var/log/nginx/access.log | tail -20
```

### 测试路径重写

```bash
# 测试 rewrite 规则（在 nginx 服务器上）
echo "GET /trans/static/css/style.css" | nc localhost 80

# 或使用 curl 查看详细信息
curl -v https://offerupup.top/trans/static/css/style.css
```

### 检查 Docker 容器

```bash
# 在 Docker 服务器上
# 检查容器是否运行
docker ps | grep translator

# 查看容器日志
docker logs translator-frontend | tail -50
docker logs translator-api | tail -50

# 进入容器测试
docker exec -it translator-frontend sh
# 或
docker exec -it translator-frontend bash

# 在容器内检查文件
ls -la /app/static/
ls -la /app/index.html
```

### 测试直接访问

```bash
# 绕过 nginx，直接访问 Docker 服务器
curl -I http://40.162.204.61:5001/
curl -I http://40.162.204.61:5001/static/css/style.css
curl -I http://40.162.204.61:5002/api/health
```

---

## 🛠️ 高级调试

### 1. 启用 Nginx 调试日志

```nginx
# 在 nginx.conf 或 server 块中
error_log /var/log/nginx/debug.log debug;

# 重载配置
sudo nginx -s reload

# 查看调试日志
sudo tail -f /var/log/nginx/debug.log
```

### 2. 使用 tcpdump 抓包

```bash
# 抓取 nginx 到 Docker 服务器的流量
sudo tcpdump -i any -nn -A 'host 40.162.204.61 and port 5001'

# 在另一个终端访问
curl https://offerupup.top/trans/
```

### 3. 使用 strace 跟踪

```bash
# 跟踪 nginx worker 进程
sudo strace -p $(pgrep -f 'nginx: worker') -s 1024 -e trace=network
```

---

## 📝 配置验证清单

- [ ] Nginx 配置语法正确（`nginx -t`）
- [ ] 已重载 Nginx 配置（`nginx -s reload`）
- [ ] Docker 容器正在运行（`docker ps`）
- [ ] 端口映射正确（5001, 5002）
- [ ] 防火墙开放端口
- [ ] 直接访问 Docker 服务器成功
- [ ] `/trans` 自动重定向到 `/trans/`
- [ ] `/trans/` 返回 200
- [ ] `/trans/static/` 资源正常加载
- [ ] `/translator-api/` API 调用成功
- [ ] 浏览器开发者工具无 404 错误
- [ ] Nginx 日志无错误

---

## 🎯 最终测试脚本

```bash
#!/bin/bash

echo "==================================="
echo "🧪 翻译服务完整测试"
echo "==================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

test_url() {
    local url=$1
    local expected=$2
    local name=$3
    
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" -eq "$expected" ]; then
        echo -e "${GREEN}✅ PASS${NC} - $name (HTTP $status)"
    else
        echo -e "${RED}❌ FAIL${NC} - $name (Expected: $expected, Got: $status)"
    fi
}

echo ""
echo "1️⃣ 测试前端访问"
test_url "https://offerupup.top/trans" 301 "前端重定向"
test_url "https://offerupup.top/trans/" 200 "前端首页"

echo ""
echo "2️⃣ 测试静态资源"
test_url "https://offerupup.top/trans/static/css/style.css" 200 "CSS 文件"
test_url "https://offerupup.top/trans/static/js/app.js" 200 "JS 文件"

echo ""
echo "3️⃣ 测试 API 端点"
test_url "https://offerupup.top/translator-api/api/health" 200 "API 健康检查"

echo ""
echo "4️⃣ 测试 CORS"
cors_headers=$(curl -s -I -X OPTIONS https://offerupup.top/translator-api/api/translate/image \
    -H "Origin: https://offerupup.top" \
    -H "Access-Control-Request-Method: POST" | grep -i "access-control")

if [ ! -z "$cors_headers" ]; then
    echo -e "${GREEN}✅ PASS${NC} - CORS 头已配置"
    echo "$cors_headers"
else
    echo -e "${RED}❌ FAIL${NC} - CORS 头缺失"
fi

echo ""
echo "==================================="
echo "测试完成！"
echo "==================================="
```

保存为 `test-translator-service.sh` 并运行：
```bash
chmod +x test-translator-service.sh
./test-translator-service.sh
```

---

## 📞 仍然有问题？

### 提供以下信息以便诊断：

1. **Nginx 错误日志：**
   ```bash
   sudo tail -50 /var/log/nginx/error.log
   ```

2. **访问日志（最近的 404）：**
   ```bash
   sudo grep "404" /var/log/nginx/access.log | tail -10
   ```

3. **浏览器开发者工具截图：**
   - Network 标签，显示 404 的请求
   - Console 标签，显示错误信息

4. **直接访问测试结果：**
   ```bash
   curl -I http://40.162.204.61:5001/
   curl -I http://40.162.204.61:5002/api/health
   ```

5. **Nginx 配置测试：**
   ```bash
   sudo nginx -t
   ```
