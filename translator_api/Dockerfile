# Image Translator API - GPU Version
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

LABEL maintainer="translator@example.com"
LABEL description="Image Translator API - Pure REST API with GPU"

WORKDIR /app

# 安装 Python 和系统依赖
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建缓存目录
RUN mkdir -p /app/models_cache /app/uploads && \
    chmod -R 777 /app/models_cache /app/uploads

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    CUDA_VISIBLE_DEVICES=0 \
    HF_HOME=/app/models_cache \
    TRANSFORMERS_CACHE=/app/models_cache \
    HF_HUB_CACHE=/app/models_cache

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5001

# 启动命令
CMD ["python3", "app.py"]
