# 🐳 Docker 快速启动

## 方式一：一键脚本（推荐）

### Windows用户

双击运行 `docker-manage.bat`，然后选择 `1` 启动所有服务：

```cmd
docker-manage.bat
```

或命令行直接启动：

```cmd
docker-manage.bat
# 然后输入 1
```

### Linux/Mac用户

```bash
# 添加执行权限
chmod +x docker-manage.sh

# 启动服务
./docker-manage.sh start

# 或进入交互式菜单
./docker-manage.sh
```

---

## 方式二：手动Docker Compose

### 1. 准备环境

确保已安装Docker：

```bash
# 检查Docker
docker --version
docker-compose --version
```

### 2. 配置环境变量（可选）

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置（可选，默认配置可直接使用）
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 3. 启动服务

```bash
# 一键启动（构建+运行）
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 等待服务启动完成（约1-2分钟）
```

### 4. 访问服务

打开浏览器：**http://localhost:5001**

---

## 🎯 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端界面 | 5001 | Web界面 |
| API服务 | 5002 | 翻译API |
| OCR服务 | 8899 | 文字识别 |
| Inpaint服务 | 8900 | 图像修复 |

---

## 📋 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f api
```

### 更新代码后重建
```bash
docker-compose down
docker-compose up -d --build
```

---

## ⚡ 第一次启动说明

**第一次运行需要：**
- 下载基础镜像（Python、系统库等）
- 安装依赖包（PyTorch、OCR库等）
- **预计时间：10-15分钟**（取决于网络速度）

**后续启动只需：**
- **10-20秒**启动容器

---

## 🔧 故障排查

### 端口被占用

修改 `.env` 文件中的端口：

```env
FRONTEND_PORT=5011
API_PORT=5012
OCR_PORT=8999
INPAINT_PORT=8901
```

### 内存不足

增加Docker内存限制（Docker Desktop → Settings → Resources）：
- **推荐：至少 4GB**
- **最佳：8GB+**

### 构建失败

```bash
# 完全清理后重新构建
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

### 查看容器内部错误

```bash
# 进入容器查看
docker exec -it translator-api bash

# 查看Python进程
ps aux | grep python

# 查看日志文件
cat /app/logs/*.log
```

---

## 🌐 生产环境部署

### 1. 配置环境变量

编辑 `.env` 文件：

```env
# 域名配置
PRODUCTION_DOMAIN=yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com

# 安全配置
MONITOR_USERNAME=admin
MONITOR_PASSWORD_HASH=your_hash_here  # 使用 python generate_password.py 生成

# AI服务（可选）
OPENAI_API_KEY=sk-...
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 配置反向代理（Nginx）

创建 `/etc/nginx/sites-available/translator`：

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # 前端
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API
    location /api {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

启用配置：

```bash
ln -s /etc/nginx/sites-available/translator /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 4. 配置HTTPS（Let's Encrypt）

```bash
apt-get install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

---

## 📊 性能优化

### GPU加速

如果有NVIDIA显卡，修改 `docker-compose.yml`：

```yaml
services:
  api:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 限制资源使用

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 💾 数据备份

### 备份数据卷

```bash
# 创建备份目录
mkdir -p backups

# 备份上传文件和日志
tar -czf backups/translator-data-$(date +%Y%m%d).tar.gz \
  translator_api/uploads \
  translator_api/archives \
  logs
```

### 导出镜像

```bash
# 保存所有镜像
docker save -o translator-images.tar \
  $(docker-compose config --services | xargs -I {} echo translator-{})

# 在新机器上加载
docker load -i translator-images.tar
```

---

## 🎉 完成！

现在你可以：
- ✅ 访问 http://localhost:5001 使用翻译服务
- ✅ 上传PDF、图片、PPT进行翻译
- ✅ 所有数据保存在本地，完全私密

**需要帮助？**
- 查看完整文档：`DOCKER_GUIDE.md`
- 查看项目说明：`README.md`
- 部署检查清单：`DEPLOYMENT_CHECKLIST.md`
