# PaddleOCR Flask API 服务

基于 PaddleOCR 3.x 和 Flask 构建的 OCR 识别 API 服务，支持中英文文字识别，提供 RESTful API 接口。

## 功能特性

- ✅ 支持中英文文字识别
- 🚀 自动检测并使用 GPU 加速
- 📱 支持 Base64 图像和 URL 图像输入
- 🔍 返回文本内容、置信度和坐标信息
- ⚡ 高性能处理，支持并发请求
- 🩺 健康状态监控
- 🌐 跨域请求支持 (CORS)

## 环境要求

- Python 3.7+
- PaddlePaddle 2.4+
- PaddleOCR 3.x
- OpenCV
- Flask

## 安装部署

### 1. 安装依赖

```bash
# 安装 PaddlePaddle (CPU版本)
pip install paddlepaddle

# 安装 PaddlePaddle (GPU版本，需要CUDA 11.2+)
pip install paddlepaddle-gpu

# 安装其他依赖
pip install paddleocr flask flask-cors opencv-python requests
```

### 2. 启动服务

```bash
python app.py
```

服务将在 `http://0.0.0.0:29001` 启动

## API 接口

### 健康检查

**GET** `/health`

```bash
curl http://localhost:29001/health
```

响应示例：
```json
{
  "status": "healthy",
  "ocr_available": true,
  "gpu_available": true,
  "startup_time": "2024-01-01T12:00:00",
  "timestamp": "2024-01-01T12:30:00",
  "version": "3.2.0",
  "performance_mode": "GPU加速",
  "message": "PaddleOCR服务运行正常 (GPU加速)"
}
```

### OCR 识别

**POST** `/ocr`

#### 请求参数

支持两种图像输入方式：

**方式一：Base64 图像**
```json
{
  "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQ..."
}
```

**方式二：图像 URL**
```json
{
  "url": "https://example.com/image.jpg"
}
```

#### 响应示例

成功响应：
```json
{
  "success": true,
  "results": [
    {
      "text": "识别文本",
      "score": 0.95,
      "points": [[10, 20], [100, 20], [100, 40], [10, 40]],
      "bbox": [10, 20, 100, 40]
    }
  ],
  "stats": {
    "total_texts": 1,
    "total_time": 0.125,
    "ocr_time": 0.098,
    "image_size": "800x600",
    "performance_mode": "GPU加速",
    "request_id": "req_1700000000000",
    "timestamp": "2024-01-01T12:30:00"
  }
}
```

错误响应：
```json
{
  "success": false,
  "error": "错误信息",
  "request_id": "req_1700000000000",
  "processing_time": 0.005,
  "performance_mode": "CPU"
}
```

## 使用示例

### Python 客户端示例

```python
import requests
import base64
import json

def ocr_from_file(image_path, api_url="http://localhost:29001/ocr"):
    """从本地文件进行OCR识别"""
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode('utf-8')
    
    data = {
        "image_base64": f"data:image/jpeg;base64,{image_base64}"
    }
    
    response = requests.post(api_url, json=data)
    return response.json()

def ocr_from_url(image_url, api_url="http://localhost:29001/ocr"):
    """从URL进行OCR识别"""
    data = {
        "url": image_url
    }
    
    response = requests.post(api_url, json=data)
    return response.json()

# 使用示例
if __name__ == "__main__":
    # 从本地文件识别
    result = ocr_from_file("test.jpg")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 从URL识别
    # result = ocr_from_url("https://example.com/image.jpg")
```

### cURL 示例

```bash
# Base64 图像识别
curl -X POST http://localhost:29001/ocr \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }'

# URL 图像识别
curl -X POST http://localhost:29001/ocr \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/image.jpg"
  }'
```

## 配置说明

### OCR 引擎配置

服务启动时自动配置 OCR 引擎：

- **语言**: 中文 (`ch`)
- **文字方向检测**: 关闭（提高速度）
- **设备**: 自动检测 GPU/CPU
- **性能优化**: 优先使用 GPU 加速

### 性能调优

如需调整性能，可修改以下参数：

```python
ocr_config = {
    'lang': 'ch',                    # 识别语言
    'use_angle_cls': False,          # 关闭文字方向检测
    'device': 'gpu',                 # 强制使用GPU
    'rec_batch_num': 16,             # 识别批处理大小
    'det_db_thresh': 0.3,            # 检测阈值
    'det_db_box_thresh': 0.5,        # 检测框阈值
}
```

## 故障排除

### 常见问题

1. **GPU 不可用**
   - 检查 CUDA 驱动安装
   - 验证 PaddlePaddle GPU 版本
   - 查看日志确认 GPU 检测结果

2. **内存不足**
   - 减小批处理大小
   - 降低图像分辨率
   - 增加系统内存

3. **识别精度低**
   - 确保图像清晰度
   - 调整检测阈值参数
   - 尝试开启文字方向检测

### 日志查看

服务运行日志包含详细的操作信息：

```
2024-01-01 12:00:00 - __main__ - INFO - ✅ PaddleOCR引擎初始化完成
2024-01-01 12:00:00 - __main__ - INFO - ⏱️  初始化耗时: 2.34秒
2024-01-01 12:00:00 - __main__ - INFO - ⚡ 测试识别耗时: 0.045秒
```

## 部署建议

### 生产环境部署

推荐使用 Gunicorn 部署：

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:29001 app:app
```

### Docker 部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install paddlepaddle paddleocr flask flask-cors opencv-python requests

EXPOSE 29001
CMD ["python", "app.py"]
```

## 许可证

MIT License

## 技术支持

如有问题，请查看：
- PaddleOCR 文档: https://github.com/PaddlePaddle/PaddleOCR
- Flask 文档: https://flask.palletsprojects.com/