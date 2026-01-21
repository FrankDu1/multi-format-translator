# 🌐 跨服务器 Nginx 配置指南

## 📋 架构说明

```
┌─────────────────┐          ┌─────────────────────────┐
│   Nginx 服务器   │ -------> │  Docker 服务器          │
│  offerupup.top  │          │  40.162.204.61         │
│                 │          │  ├─ translator-api:5002 │
│                 │          │  └─ translator-frontend:5001 │
└─────────────────┘          └──────────────────────────┘
```

## 🔧 配置步骤

### 1. 获取 Docker 服务器 IP 地址

```bash
# 在 Docker 服务器上查看 IP
ip addr show | grep inet

# 或者
hostname -I

# 假设得到 IP：40.162.204.61
```

### 2. 更新 nginx 配置变量

编辑 `nginx-config-update.conf`，修改这两行：

```nginx
set $translator_api_host "40.162.204.61:5002";       # ⚠️ 改为你的实际 IP
set $translator_frontend_host "40.162.204.61:5001";  # ⚠️ 修改为你的实际 IP
```

### 3. 确保 Docker 容器端口暴露

**检查 docker-compose.yml：**

```yaml
services:
  translator-frontend:
    ports:
      - "5001:5001"  # ✅ 必须暴露到宿主机
  
  translator-api:
    ports:
      - "5002:5002"  # ✅ 必须暴露到宿主机
```

**启动容器：**
```bash
docker-compose up -d
```

### 4. 开放防火墙端口

**在 Docker 服务器上（40.162.204.61）：**

#### Ubuntu/Debian (ufw):
```bash
# 开放端口
sudo ufw allow 5001/tcp
sudo ufw allow 5002/tcp

# 查看状态
sudo ufw status
```

#### CentOS/RHEL (firewalld):
```bash
# 开放端口
sudo firewall-cmd --add-port=5001/tcp --permanent
sudo firewall-cmd --add-port=5002/tcp --permanent
sudo firewall-cmd --reload

# 查看状态
sudo firewall-cmd --list-ports
```

#### 云服务器安全组：
如果使用阿里云、AWS、Azure 等，需要在控制台添加安全组规则：
- 入站规则：TCP 5001
- 入站规则：TCP 5002

### 5. 测试连接

**在 Nginx 服务器上测试：**

```bash
# 测试前端连通性
curl -I http://40.162.204.61:5001

# 测试 API 连通性
curl -I http://40.162.204.61:5002/api/health

# 测试网络连通性
ping 40.162.204.61
telnet 40.162.204.61 5001
telnet 40.162.204.61 5002
```

**预期结果：**
```
HTTP/1.1 200 OK
或
HTTP/1.0 200 OK
```

### 6. 部署 Nginx 配置

```bash
# 1. 上传配置文件到 nginx 服务器
scp nginx-config-update.conf user@nginx-server:/tmp/

# 2. SSH 到 nginx 服务器
ssh user@nginx-server

# 3. 备份原配置
sudo cp /etc/nginx/sites-available/offerupup.top /etc/nginx/sites-available/offerupup.top.backup

# 4. 修改配置文件中的 IP 地址
sudo nano /tmp/nginx-config-update.conf
# 找到并修改：
# set $translator_api_host "YOUR_DOCKER_SERVER_IP:5002";
# set $translator_frontend_host "YOUR_DOCKER_SERVER_IP:5001";

# 5. 移动配置文件
sudo mv /tmp/nginx-config-update.conf /etc/nginx/sites-available/offerupup.top

# 6. 测试配置
sudo nginx -t

# 7. 重载 nginx
sudo nginx -s reload
```

### 7. 验证部署

```bash
# 访问前端
curl -I https://offerupup.top/trans

# 测试 API
curl -X OPTIONS https://offerupup.top/translator-api/api/translate/image \
  -H "Origin: https://offerupup.top" \
  -H "Access-Control-Request-Method: POST" \
  -i
```

---

## 🔒 安全配置（推荐）

### 方案 1：限制访问源 IP

**在 Docker 服务器防火墙配置：**

```bash
# 获取 Nginx 服务器 IP（假设是 1.2.3.4）
# 只允许 nginx 服务器访问

sudo ufw delete allow 5001/tcp
sudo ufw delete allow 5002/tcp

sudo ufw allow from 1.2.3.4 to any port 5001
sudo ufw allow from 1.2.3.4 to any port 5002
```

### 方案 2：使用 VPN 或内网

如果两台服务器在同一个云服务商：
- 使用内网 IP（如 10.x.x.x 或 172.x.x.x）
- 速度更快，更安全

```nginx
set $translator_api_host "10.0.0.5:5002";       # 内网 IP
set $translator_frontend_host "10.0.0.5:5001";  # 内网 IP
```

### 方案 3：SSH 隧道（高安全场景）

**在 Nginx 服务器上建立隧道：**

```bash
# 建立 SSH 隧道
ssh -fN -L 5001:localhost:5001 user@docker-server
ssh -fN -L 5002:localhost:5002 user@docker-server

# 配置使用 localhost
set $translator_api_host "localhost:5002";
set $translator_frontend_host "localhost:5001";
```

---

## 📊 性能优化

### 1. 启用 Keepalive

```nginx
upstream translator_api {
    server 40.162.204.61:5002 max_fails=3 fail_timeout=30s;
    keepalive 32;
    keepalive_timeout 60s;
}

upstream translator_frontend {
    server 40.162.204.61:5001 max_fails=3 fail_timeout=30s;
    keepalive 32;
    keepalive_timeout 60s;
}

location /translator-api/ {
    proxy_pass http://translator_api/;
    proxy_http_version 1.1;
    proxy_set_header Connection "";
}
```

### 2. 启用压缩

```nginx
# 在 nginx 主配置添加
gzip on;
gzip_proxied any;
gzip_types text/plain text/css application/json application/javascript;
```

---

## ❓ 常见问题

### Q1: 502 Bad Gateway
**原因：** 无法连接到 Docker 服务器

**排查：**
```bash
# 1. 检查 Docker 容器是否运行
ssh docker-server
docker ps | grep translator

# 2. 检查端口是否监听
netstat -tlnp | grep 500

# 3. 检查防火墙
sudo ufw status
sudo iptables -L -n

# 4. 测试从 nginx 服务器的连接
curl -I http://docker-server-ip:5001
```

### Q2: 504 Gateway Timeout
**原因：** 请求超时

**解决：**
```nginx
# 增加超时时间（已在配置中）
proxy_connect_timeout 300;
proxy_read_timeout 300;
proxy_send_timeout 300;
```

### Q3: CORS 错误
**原因：** 跨域配置未生效

**检查：**
```bash
# 查看响应头
curl -I https://offerupup.top/translator-api/api/translate/image

# 应该包含：
# Access-Control-Allow-Origin: *
```

### Q4: 文件上传失败
**原因：** 文件太大

**解决：**
```nginx
# nginx 配置（已添加）
client_max_body_size 100M;
```

同时检查 Docker 服务器的 Flask 配置。

---

## 📝 配置检查清单

部署前检查：

- [ ] 获取 Docker 服务器 IP 地址
- [ ] 修改 nginx 配置中的 IP 地址
- [ ] Docker 容器端口映射正确（5001, 5002）
- [ ] 防火墙开放端口（5001, 5002）
- [ ] 云服务商安全组配置（如适用）
- [ ] 从 nginx 服务器测试连接成功
- [ ] Nginx 配置语法测试通过
- [ ] 重载 nginx 配置
- [ ] 前端访问测试
- [ ] API 访问测试
- [ ] CORS 测试
- [ ] 文件上传测试

---

## 🔗 完整配置示例

**nginx-config-update.conf:**

```nginx
set $translator_api_host "40.162.204.61:5002";
set $translator_frontend_host "40.162.204.61:5001";

location /translator-api/ {
    proxy_pass http://$translator_api_host/;
    # ... CORS 配置 ...
}

location /trans {
    proxy_pass http://$translator_frontend_host;
    # ... 其他配置 ...
}
```

**docker-compose.yml:**

```yaml
services:
  translator-frontend:
    image: ghcr.io/frankdu1/translator-frontend:latest
    ports:
      - "5001:5001"
    restart: always
  
  translator-api:
    image: ghcr.io/frankdu1/translator-api:latest
    ports:
      - "5002:5002"
    restart: always
```

---

## 🎯 测试命令

```bash
# 完整测试流程
echo "1. 测试 Docker 服务器连通性"
ping -c 3 40.162.204.61

echo "2. 测试端口连通性"
nc -zv 40.162.204.61 5001
nc -zv 40.162.204.61 5002

echo "3. 测试 HTTP 响应"
curl -I http://40.162.204.61:5001
curl -I http://40.162.204.61:5002/api/health

echo "4. 测试通过 nginx 访问"
curl -I https://offerupup.top/trans
curl -I https://offerupup.top/translator-api/api/translate/image

echo "5. 测试 CORS"
curl -X OPTIONS https://offerupup.top/translator-api/api/translate/image \
  -H "Origin: https://offerupup.top" \
  -H "Access-Control-Request-Method: POST" \
  -i
```

---

## 📞 故障排查

```bash
# Nginx 服务器日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker 服务器日志
docker logs -f translator-frontend
docker logs -f translator-api

# 网络测试
traceroute 40.162.204.61
mtr 40.162.204.61

# 防火墙状态
sudo ufw status verbose
sudo iptables -L -n -v
```
