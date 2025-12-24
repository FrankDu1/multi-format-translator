# ============================================
# Inpaint 服务 Dockerfile (GPU 版本)
# 需要 NVIDIA Docker Runtime
# ============================================
FROM docker.m.daocloud.io/nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

LABEL maintainer="inpaint-service"
LABEL description="智能图片文字移除服务 (GPU 加速)"

WORKDIR /app

# 环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HOST=0.0.0.0 \
    PORT=29002 \
    LOG_LEVEL=INFO \
    DEBIAN_FRONTEND=noninteractive

# 使用清华大学镜像源（更稳定）
RUN sed -i 's@//.*archive.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list && \
    sed -i 's@//.*security.ubuntu.com@//mirrors.tuna.tsinghua.edu.cn@g' /etc/apt/sources.list && \
    cat /etc/apt/sources.list

# 安装 Python 和系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建 python 软链接
RUN ln -sf /usr/bin/python3 /usr/bin/python

# 升级 pip 并安装 Python 依赖（使用清华源）
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn && \
    python3 -m pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 验证安装
RUN python3 -c "import flask; import cv2; import numpy; print('All modules installed successfully')"

# 复制应用代码
COPY app.py .
COPY start.sh .
COPY README.md .

# 设置脚本权限
RUN chmod +x start.sh

# 非 root 用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 29002

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:29002/health', timeout=5)" || exit 1

# 使用生产环境启动脚本
CMD ["./start.sh"]
