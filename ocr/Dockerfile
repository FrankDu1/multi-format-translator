# 使用Python官方镜像（与其他服务保持一致）
# 可选：GPU版本使用 nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
FROM python:3.10-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# 安装系统依赖（PaddleOCR需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 安装Python依赖
# 先升级pip和安装wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 安装PaddlePaddle CPU版本（使用官方源更稳定）
RUN pip install --no-cache-dir paddlepaddle==2.6.1 || \
    pip install --no-cache-dir paddlepaddle || \
    pip install --no-cache-dir paddlepaddle==2.5.2

# 安装PaddleOCR
RUN pip install --no-cache-dir paddleocr

# 安装其他依赖
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /var/log/ocr-service

EXPOSE 8899

CMD ["python", "app.py"]