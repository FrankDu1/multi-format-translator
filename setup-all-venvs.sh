#!/bin/bash
# filepath: ~/trans_web_app/setup-all-venvs.sh

echo "========================================="
echo "  为所有服务创建虚拟环境"
echo "========================================="
echo ""

cd ~/trans_web_app

# ========== 1. OCR 服务 ==========
echo "[1/3] 设置 OCR 服务虚拟环境..."
cd ~/trans_web_app/ocr

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ OCR venv 已创建"
else
    echo "⚠️  OCR venv 已存在，跳过"
fi

# 激活并安装依赖
source venv/bin/activate
pip install --upgrade pip

# 从你的好用的环境导出依赖
cat > requirements.txt << 'EOF'
paddlepaddle-gpu==3.2.0
paddleocr==3.2.0
paddlex==3.2.1
flask==3.1.2
flask-cors==6.0.1
opencv-contrib-python==4.10.0.84
numpy==2.2.6
pillow==11.3.0
pyclipper==1.3.0.post6
shapely==2.1.2
requests==2.32.5
tqdm==4.67.1
pyyaml==6.0.2
EOF

pip install -r requirements.txt
deactivate
echo "✅ OCR 依赖安装完成"
echo ""

# ========== 2. Inpaint 服务 ==========
echo "[2/3] 设置 Inpaint 服务虚拟环境..."
cd ~/trans_web_app/inpaint

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Inpaint venv 已创建"
else
    echo "⚠️  Inpaint venv 已存在，跳过"
fi

source venv/bin/activate
pip install --upgrade pip
# 根据 inpaint 服务需要安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ Inpaint 依赖安装完成"
fi
deactivate
echo ""

# ========== 3. API 服务 ==========
echo "[3/3] 设置 API 服务虚拟环境..."
cd ~/trans_web_app/translator_api

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ API venv 已创建"
else
    echo "⚠️  API venv 已存在，跳过"
fi

source venv/bin/activate
pip install --upgrade pip
# 根据 API 服务需要安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✅ API 依赖安装完成"
fi
deactivate
echo ""

echo "========================================="
echo "✅ 所有虚拟环境设置完成！"
echo "========================================="
echo ""
echo "📌 使用方式:"
echo "   cd ~/trans_web_app/ocr"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
