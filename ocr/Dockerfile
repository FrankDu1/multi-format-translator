# 使用官方PaddlePaddle镜像（阿里云环境可访问）
#FROM ccr-2vdh3abv-pub.cnc.bj.baidubce.com/paddlepaddle/paddle:3.0.0-gpu-cuda11.8-cudnn8.9-trt8.6
FROM crpi-ppdkw6cnzgorx75r.cn-hangzhou.personal.cr.aliyuncs.com/general_offerupup/paddlegpucuda11.8cudnn8.9trt8.6:latest

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 安装Python依赖
RUN python -m pip install paddleocr
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /var/log/ocr-service

EXPOSE 29001

CMD ["python", "app.py"]