# 部署检查清单 / Deployment Checklist

在部署到生产环境之前，请确保完成以下检查项。

## 📋 环境配置检查

### 必需配置

- [ ] 复制 `.env.example` 为 `.env`
- [ ] 设置 `PRODUCTION_DOMAIN` 为你的域名
- [ ] 运行 `python generate_password.py` 生成监控密码
- [ ] 将生成的哈希值设置到 `MONITOR_PASSWORD_HASH`
- [ ] 如需 AI 功能，配置 `OPENAI_API_KEY`

### 可选配置

- [ ] 自定义服务端口（如有冲突）
- [ ] 配置 `ALLOWED_ORIGINS` 允许的 CORS 源
- [ ] 配置 `MAX_FILE_SIZE` 最大文件大小
- [ ] 配置 `OLLAMA_BASE_URL`（如使用 Ollama）

## 🐳 Docker 部署检查

### 构建前

- [ ] 确认 Docker 和 Docker Compose 已安装
- [ ] 检查 `.env` 文件配置正确
- [ ] 确认端口未被占用

### 构建

```bash
# 构建镜像
docker-compose build

# 检查镜像
docker images | grep translator
```

### 启动

```bash
# 启动服务
docker-compose up -d

# 检查服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 验证

- [ ] 所有容器都在运行：`docker-compose ps`
- [ ] OCR 服务健康检查：`curl http://localhost:8899/health`
- [ ] Inpaint 服务健康检查：`curl http://localhost:8900/health`
- [ ] API 服务健康检查：`curl http://localhost:5002/api/health`
- [ ] 前端可访问：打开 `http://localhost:5001`

## 🖥️ 本地部署检查

### 依赖安装

```bash
# 检查 Python 版本
python --version  # 应该 >= 3.8

# 安装依赖
cd translator_api && pip install -r requirements.txt
cd ../ocr && pip install -r requirements.txt
cd ../inpaint && pip install -r requirements.txt
```

### 启动服务

**Windows:**
```cmd
manage-services.bat
# 选择 1 启动所有服务
```

**Linux/Mac:**
```bash
chmod +x start-all-dev.sh
./start-all-dev.sh
```

### 验证

- [ ] 所有服务启动成功，无错误日志
- [ ] 访问 `http://localhost:5001` 能看到界面
- [ ] 尝试翻译功能正常工作

## 🔒 安全检查

### 生产环境

- [ ] 修改默认监控密码
- [ ] 限制 `ALLOWED_ORIGINS` 仅允许你的域名
- [ ] 不要在代码中硬编码任何密钥
- [ ] 使用 HTTPS（通过 Nginx 反向代理）
- [ ] 定期更新依赖包

### API 密钥

- [ ] `OPENAI_API_KEY` 已设置且有效（如使用）
- [ ] API 密钥不要提交到 Git
- [ ] 使用环境变量或密钥管理服务

## 📊 性能检查

### 资源

- [ ] 确认服务器有足够的内存（建议至少 4GB）
- [ ] 如有 GPU，确认 CUDA 驱动已安装
- [ ] 磁盘空间充足（用于日志和上传文件）

### 优化

- [ ] 配置合适的 `MAX_FILE_SIZE`
- [ ] 考虑使用 Redis 缓存（未来功能）
- [ ] 监控日志文件大小，定期清理

## 🌐 网络配置

### 域名和 SSL

- [ ] 域名已解析到服务器
- [ ] SSL 证书已配置（推荐使用 Let's Encrypt）
- [ ] Nginx 反向代理已配置

### 防火墙

- [ ] 开放必要的端口（80/443 用于 Web）
- [ ] 内部服务端口不对外暴露
- [ ] 配置 fail2ban 防止暴力破解

## 📝 文档检查

- [ ] README 已更新，包含实际的部署信息
- [ ] 团队成员知道如何访问和使用服务
- [ ] 记录了常见问题和解决方案

## 🔄 备份和恢复

- [ ] 配置了自动备份（上传文件、数据库等）
- [ ] 测试过恢复流程
- [ ] 有灾难恢复计划

## 📈 监控和日志

- [ ] 日志正常输出到 `logs/` 目录
- [ ] 设置日志轮转（避免磁盘满）
- [ ] 配置监控告警（可选）
- [ ] 能访问监控面板（如配置了）

## ✅ 最终验证

### 功能测试

- [ ] 文本翻译正常
- [ ] 图片翻译正常
- [ ] PDF 翻译正常
- [ ] PPT 翻译正常
- [ ] AI 总结功能正常（如启用）

### 压力测试

- [ ] 并发请求能正常处理
- [ ] 大文件上传正常（在限制内）
- [ ] 服务在高负载下稳定

## 🎉 部署完成

完成所有检查后：

1. 记录服务访问地址
2. 通知团队成员
3. 准备用户文档
4. 开始使用！

---

## 🆘 遇到问题？

- 检查日志：`docker-compose logs` 或 `logs/` 目录
- 查看 [QUICKSTART.md](QUICKSTART.md) 快速开始指南
- 查看 [README.md](README.md) 完整文档
- 提交 Issue：https://github.com/FrankDu1/multi-format-translator/issues
