# Inpaint 服务

智能移除图片中指定区域的文字，基于 OpenCV inpainting 算法。

## ✨ 特性

- 🎨 智能图像修复 (OpenCV Inpainting)
- 🚀 支持 GPU 加速 (CUDA)
- 🐳 Docker 容器化部署
- 📦 支持两种 boxes 格式
- ✅ 完整的错误处理和日志
- 🔧 环境变量配置

## 🚀 快速开始

### 直接运行

```bash
pip install -r requirements.txt
python main.py
```

### Docker (CPU)

```bash
docker-compose up -d inpaint-cpu
```

### Docker (GPU)

```bash
docker-compose --profile gpu up -d inpaint-gpu
```

## 📖 API 文档

### POST /inpaint

**请求**: `multipart/form-data`
- `file`: 图片文件
- `boxes`: JSON 格式坐标数组

**Boxes 格式**:
```json
[
  [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
]
```

**响应**: 处理后的 JPEG 图片或 JSON 错误

### GET /health

健康检查端点

## 💡 使用示例

```python
import requests, json

boxes = [[[100, 50], [300, 50], [300, 100], [100, 100]]]
with open('test.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:29002/inpaint',
        files={'file': f},
        data={'boxes': json.dumps(boxes)}
    )
with open('output.jpg', 'wb') as f:
    f.write(response.content)
```

## ⚙️ 配置

| 变量 | 默认值 | 说明 |
|------|--------|------|
| HOST | 0.0.0.0 | 监听地址 |
| PORT | 29002 | 监听端口 |
| LOG_LEVEL | INFO | 日志级别 |
| INPAINT_METHOD | TELEA | 修复算法 (TELEA/NS) |
| INPAINT_RADIUS | 3 | 修复半径 |
| OUTPUT_QUALITY | 95 | 输出质量 |

## 🐧 Linux + GPU 部署

### 安装 nvidia-docker

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 部署

```bash
docker build -f Dockerfile.gpu -t inpaint-gpu .
docker run -d --gpus all -p 29002:29002 inpaint-gpu
```

## 🧪 测试

```bash
python test.py
```

## 📝 日志示例

```
2024-10-16 08:55:45 - [INFO] - [20241016_085545] 收到 inpaint 请求
2024-10-16 08:55:46 - [INFO] - [20241016_085545] ✓ 完成: 1.234s
```

## 📄 许可证

MIT License

---
**版本**: 1.0.0 | **更新**: 2024-10-16
