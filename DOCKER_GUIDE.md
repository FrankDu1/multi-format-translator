# 🐳 Docker 一键部署指南

## ✅ 你的项目已经有完整的Docker配置！

这个项目已经包含了所有必要的Docker配置文件，可以一键打包部署。

## 📦 包含的服务

你的 `docker-compose.yml` 已经配置好了4个服务：

1. **OCR服务** (端口 8899) - 文字识别
2. **Inpaint服务** (端口 8900) - 图像修复
3. **API服务** (端口 5002) - 翻译API
4. **前端服务** (端口 5001) - Web界面

## 🚀 快速启动（3步）

### 步骤1：确保安装 Docker

```bash
# 检查Docker是否安装
docker --version
docker-compose --version
```

如果未安装，请访问：https://www.docker.com/get-started

### 步骤2：配置环境变量（可选）

```bash
# 复制环境变量模板（如果存在）
cp .env.example .env

# 或手动创建 .env 文件，内容如下：
```

创建 `.env` 文件：
```env
# 端口配置
FRONTEND_PORT=5001
API_PORT=5002
OCR_PORT=8899
INPAINT_PORT=8900

# CORS配置
ALLOWED_ORIGINS=http://localhost:5001

# 日志级别
LOG_LEVEL=INFO

# AI服务（可选）
# OPENAI_API_KEY=your_key_here
# OPENAI_BASE_URL=https://api.openai.com/v1
# OLLAMA_BASE_URL=http://localhost:11434

# 监控面板
MONITOR_USERNAME=admin
# MONITOR_PASSWORD_HASH=your_hash_here

# 文件大小限制（字节）
MAX_FILE_SIZE=16777216

# 生产环境域名（可选）
# PRODUCTION_DOMAIN=yourdomain.com
```

### 步骤3：一键启动

```bash
# 构建并启动所有服务（第一次运行需要几分钟）
docker-compose up -d

# 查看启动日志
docker-compose logs -f

# 等待所有服务启动完成
```

### 步骤4：访问服务

打开浏览器访问：**http://localhost:5001**

## 📋 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f api
docker-compose logs -f ocr
docker-compose logs -f inpaint
docker-compose logs -f frontend
```

### 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart api
```

### 更新代码后重新构建
```bash
# 停止服务
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

### 清理无用镜像
```bash
docker system prune -a
```

## 🔧 故障排查

### 1. 端口被占用

如果端口被占用，修改 `.env` 文件中的端口号：
```env
FRONTEND_PORT=5011
API_PORT=5012
OCR_PORT=8999
INPAINT_PORT=8901
```

### 2. 内存不足

如果构建失败，增加Docker内存限制：
- Docker Desktop → Settings → Resources → Memory → 至少 4GB

### 3. 网络问题

如果拉取镜像慢，可以配置Docker镜像加速：
- 参考 `inpaint/DOCKER_MIRROR_GUIDE.md`

### 4. 查看容器内部
```bash
# 进入容器
docker exec -it translator-api bash

# 查看容器资源使用
docker stats
```

## 📊 服务健康检查

```bash
# 检查OCR服务
curl http://localhost:8899/health

# 检查Inpaint服务
curl http://localhost:8900/health

# 检查API服务
curl http://localhost:5002/api/health
```

## 🌐 生产环境部署

### 1. 使用域名

修改 `.env` 文件：
```env
PRODUCTION_DOMAIN=yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. 配置反向代理（推荐使用Nginx）

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. 启用HTTPS（Let's Encrypt）

```bash
# 安装certbot
apt-get install certbot python3-certbot-nginx

# 申请证书
certbot --nginx -d yourdomain.com
```

## 🎯 性能优化

### 1. GPU加速（如果有NVIDIA显卡）

需要安装 NVIDIA Container Toolkit，然后修改 `docker-compose.yml`：

```yaml
services:
  api:
    # ... 其他配置
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 2. 数据持久化

默认配置已经包含数据卷：
- `./logs` - 日志文件
- `./translator_api/uploads` - 上传文件
- `./translator_api/archives` - 归档文件

## 📦 导出/备份

### 导出Docker镜像
```bash
# 保存镜像到文件
docker save -o translator-images.tar \
  translator-api \
  translator-ocr \
  translator-inpaint \
  translator-frontend

# 在另一台机器上加载
docker load -i translator-images.tar
```

### 备份数据
```bash
# 备份上传文件和日志
tar -czf translator-data-backup.tar.gz \
  translator_api/uploads \
  translator_api/archives \
  logs
```

## 🎉 完成！

现在你可以：
1. 访问 http://localhost:5001 使用翻译服务
2. 上传PDF、图片、PPT进行翻译
3. 所有数据都在本地，不会上传到外部服务

**需要帮助？** 查看项目的其他文档：
- `README.md` - 完整功能说明
- `QUICKSTART.md` - 快速入门
- `DEPLOYMENT_CHECKLIST.md` - 部署检查清单
