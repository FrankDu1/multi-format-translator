# 🚀 GitHub Actions Docker 快速配置

## ⚡ 3步完成自动构建

### 步骤1：配置Docker Hub Secrets

进入GitHub仓库：**Settings → Secrets → Actions**

添加2个secrets：

```
DOCKER_USERNAME = 你的Docker Hub用户名
DOCKER_PASSWORD = 你的Docker Hub Access Token
```

**获取Docker Hub Token：**
1. 登录 https://hub.docker.com/
2. Account Settings → Security → New Access Token
3. 复制Token（只显示一次！）

---

### 步骤2：推送代码

```bash
# 提交workflow文件
git add .github/
git commit -m "ci: 添加Docker自动构建"
git push origin main
```

---

### 步骤3：查看构建

访问：**GitHub仓库 → Actions**

等待构建完成（约15-20分钟）

---

## 🎯 触发方式

### 自动触发

**Push到main/develop分支：**
```bash
git push origin main
# → 自动构建所有4个Docker镜像
# → 推送到Docker Hub
```

**创建版本Tag：**
```bash
git tag v1.0.0
git push origin v1.0.0
# → 构建镜像，标签为 v1.0.0 和 latest
# → 自动创建GitHub Release
```

### 手动触发

1. 访问：**Actions → Manual Docker Publish**
2. 点击：**Run workflow**
3. 选择服务和标签
4. 点击：**Run workflow**

---

## 🐳 使用构建的镜像

### 拉取镜像

```bash
docker pull yourname/translator-frontend:latest
docker pull yourname/translator-api:latest
docker pull yourname/translator-ocr:latest
docker pull yourname/translator-inpaint:latest
```

### 启动服务

```bash
# 直接使用Docker Hub镜像
docker-compose up -d
```

---

## 📋 生成的镜像标签

| 操作 | 镜像标签 |
|------|---------|
| Push到main | `latest`, `main` |
| Push到develop | `develop` |
| Tag v1.2.3 | `v1.2.3`, `1.2`, `1`, `latest` |

---

## 🔍 故障排查

### 认证失败

✅ 检查Secrets是否正确配置  
✅ 使用Access Token，不是密码

### 构建失败

✅ 查看Actions日志  
✅ 检查Dockerfile是否有错误

### 推送失败

✅ 检查Docker Hub配额  
✅ 确认Token有写入权限

---

## 🎉 完成！

现在每次push代码都会自动：
- ✅ 构建Docker镜像
- ✅ 推送到Docker Hub
- ✅ 运行测试
- ✅ 创建Release（如果是tag）

**详细文档：** 查看 `.github/DOCKER_SETUP.md`
