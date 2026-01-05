# OCR服务 Docker说明

## 镜像版本选择

### 1. CPU版本（默认，用于CI/CD）
**文件：** `Dockerfile`  
**基础镜像：** `python:3.10-slim`

**优点：**
- ✅ 通用性强，任何环境都能运行
- ✅ 镜像体积小（约300MB）
- ✅ GitHub Actions可构建
- ✅ 无需GPU驱动

**缺点：**
- ⚠️ OCR速度较慢

**使用场景：**
- GitHub Actions自动构建
- 无GPU的服务器
- 开发测试环境

**构建：**
```bash
docker build -t ocr-service:cpu -f Dockerfile .
```

---

### 2. GPU版本（本地部署推荐）
**文件：** `Dockerfile.gpu`  
**基础镜像：** `nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04`

**优点：**
- ✅ OCR速度快（5-10倍）
- ✅ 支持批量处理
- ✅ 生产环境推荐

**缺点：**
- ⚠️ 需要NVIDIA GPU
- ⚠️ 需要nvidia-docker
- ⚠️ 镜像体积大（约2GB）

**使用场景：**
- 有GPU的本地服务器
- 生产环境部署
- 高并发OCR需求

**构建：**
```bash
docker build -t ocr-service:gpu -f Dockerfile.gpu .
```

**运行（需要nvidia-docker）：**
```bash
docker run --gpus all -p 8899:8899 ocr-service:gpu
```

---

### 3. 自定义版本（阿里云等特定环境）
**文件：** `Dockerfile.custom`（自行创建）

如果你在特定云环境（如阿里云）有专用镜像：
```dockerfile
FROM crpi-xxx.aliyuncs.com/your-image:latest
# ... 保持原有配置
```

---

## 在docker-compose中选择版本

### CPU版本（默认）
```yaml
services:
  ocr:
    build:
      context: ./ocr
      dockerfile: Dockerfile  # CPU版本
```

### GPU版本
```yaml
services:
  ocr:
    build:
      context: ./ocr
      dockerfile: Dockerfile.gpu  # GPU版本
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

## 性能对比

| 版本 | 单张图片OCR | 10张批量 | 内存占用 |
|------|-----------|----------|---------|
| CPU | ~3-5秒 | ~30-50秒 | ~500MB |
| GPU | ~0.5-1秒 | ~5-10秒 | ~2GB |

---

## 推荐配置

### 开发环境
```bash
# 使用CPU版本
docker-compose up -d
```

### 生产环境（有GPU）
```bash
# 修改docker-compose.yml使用Dockerfile.gpu
# 然后启动
docker-compose up -d
```

### GitHub Actions
- 自动使用CPU版本（Dockerfile）
- 无需修改

---

## 切换到GPU版本

如果你本地有NVIDIA GPU，想使用GPU加速：

**步骤1：** 修改 `docker-compose.yml`

```yaml
ocr:
  build:
    context: ./ocr
    dockerfile: Dockerfile.gpu  # 改这里
```

**步骤2：** 重新构建

```bash
docker-compose build ocr
docker-compose up -d ocr
```

**步骤3：** 验证GPU使用

```bash
# 查看GPU使用情况
nvidia-smi

# 查看容器日志
docker-compose logs ocr
```

---

## 故障排查

### CPU版本慢怎么办？

1. **增加并发处理**
   - 修改 `app.py`，启用多线程

2. **使用GPU版本**
   - 如果有GPU，切换到 `Dockerfile.gpu`

3. **优化图片大小**
   - 压缩输入图片
   - 限制最大尺寸

### GPU版本无法启动

1. **检查nvidia-docker**
   ```bash
   docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
   ```

2. **检查CUDA版本**
   ```bash
   nvidia-smi  # 查看CUDA版本
   ```

3. **降级CUDA镜像**
   如果你的GPU不支持CUDA 11.8，修改为：
   ```dockerfile
   FROM nvidia/cuda:11.2.0-cudnn8-runtime-ubuntu20.04
   ```

---

## 镜像清单

| 镜像 | 用途 | 大小 | 速度 |
|------|------|------|------|
| `python:3.10-slim` | 通用CPU | 约300MB | 慢 |
| `nvidia/cuda:11.8.0-cudnn8-runtime` | GPU加速 | 约2GB | 快 |
| 你的私有镜像 | 定制环境 | 取决于配置 | 取决于配置 |

---

## 推荐方案

**如果你要推送到GitHub：**
- ✅ 使用 `Dockerfile`（CPU版本）
- ✅ 让GitHub Actions自动构建
- ✅ 镜像可以在任何环境运行

**如果本地部署且有GPU：**
- ✅ 本地使用 `Dockerfile.gpu`
- ✅ docker-compose使用GPU版本
- ✅ 获得最佳性能

**混合方案：**
- GitHub Actions构建CPU版本
- 本地docker-compose使用GPU版本
- 两个版本共存
