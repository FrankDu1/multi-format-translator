# ============================================
# Inpaint 服务 Dockerfile (CPU 版本 - 通用)
# ============================================
FROM python:3.10-slim

LABEL maintainer="inpaint-service"
LABEL description="智能图片文字移除服务"

WORKDIR /app

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=8900 \
    LOG_LEVEL=INFO

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY app.py .

# 创建日志目录
RUN mkdir -p /var/log/inpaint-service

EXPOSE 8900

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8900/health || exit 1

CMD ["python", "app.py"]
