#!/bin/bash
# filepath: ~/trans_web_app/manage-services.sh

show_menu() {
    clear
    echo "========================================="
    echo "     翻译服务管理菜单 (后台模式)"
    echo "========================================="
    echo ""
    echo "  1. 启动所有服务"
    echo "  2. 停止所有服务"
    echo "  3. 重启所有服务"
    echo "  4. 查看服务状态"
    echo "  5. 查看日志文件"
    echo "  6. 查看实时日志 (tail -f)"
    echo "  7. 健康检查"
    echo "  8. 清理日志文件"
    echo "  9. 🔧 搭建开发环境 (Setup)"
    echo " 10. 重启单个服务"
    echo "  0. 退出"
    echo ""
    echo "========================================="
    echo -n "请选择操作 (0-10): "
}

# ==========================================
# 🔥 新增：搭建开发环境
# ==========================================
setup_environment() {
    clear
    echo ""
    echo "========================================="
    echo "  🔧 搭建开发环境"
    echo "========================================="
    echo ""
    
    # 检测操作系统
    detect_os
    
    echo "📋 将执行以下操作："
    echo ""
    echo "  1. 检查系统依赖 (Python, Git, etc.)"
    echo "  2. 创建 Python 虚拟环境 (venv)"
    echo "  3. 安装 Python 依赖包"
    echo "  4. 下载 AI 模型文件"
    echo "  5. 创建必要的目录结构"
    echo "  6. 配置环境变量"
    echo ""
    echo "⏱️  预计耗时: 10-30 分钟 (取决于网络速度)"
    echo ""
    read -p "确认继续? (y/n): " confirm
    
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo ""
        echo "❌ 已取消操作"
        echo ""
        read -p "按Enter键继续..."
        return
    fi
    
    echo ""
    echo "========================================="
    echo "🚀 开始搭建环境..."
    echo "========================================="
    echo ""
    
    # 执行各个步骤
    check_system_dependencies
    create_virtual_environments
    install_python_packages
    download_models
    create_directories
    setup_config_files
    
    echo ""
    echo "========================================="
    echo "✅ 开发环境搭建完成！"
    echo "========================================="
    echo ""
    echo "📋 下一步操作："
    echo ""
    echo "  1. 启动所有服务:   选择菜单 [1]"
    echo "  2. 查看服务状态:   选择菜单 [4]"
    echo "  3. 健康检查:       选择菜单 [7]"
    echo ""
    echo "🌐 访问地址:"
    echo "  前端界面: http://localhost:5001"
    echo "  API文档:  http://localhost:29003/docs"
    echo ""
    read -p "按Enter键继续..."
}

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS_TYPE="Linux"
        # 检测发行版
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS_DISTRO=$NAME
            echo "🖥️  检测到系统: $OS_DISTRO"
        else
            OS_DISTRO="Linux"
            echo "🖥️  检测到系统: Linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS_TYPE="macOS"
        OS_DISTRO="macOS"
        echo "🖥️  检测到系统: macOS"
    else
        OS_TYPE="Unknown"
        OS_DISTRO="Unknown"
        echo "⚠️  未知系统类型: $OSTYPE"
    fi
    echo ""
}

# 检查系统依赖
check_system_dependencies() {
    echo "[1/6] 检查系统依赖..."
    echo ""
    
    local missing_deps=()
    
    # 检查 Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo "✅ Python3: $PYTHON_VERSION"
    else
        echo "❌ Python3: 未安装"
        missing_deps+=("python3")
    fi
    
    # 检查 pip
    if command -v pip3 &> /dev/null; then
        echo "✅ pip3: 已安装"
    else
        echo "❌ pip3: 未安装"
        missing_deps+=("python3-pip")
    fi
    
    # 检查 git
    if command -v git &> /dev/null; then
        echo "✅ git: 已安装"
    else
        echo "❌ git: 未安装"
        missing_deps+=("git")
    fi
    
    # 检查 curl
    if command -v curl &> /dev/null; then
        echo "✅ curl: 已安装"
    else
        echo "❌ curl: 未安装"
        missing_deps+=("curl")
    fi
    
    # 检查 lsof
    if command -v lsof &> /dev/null; then
        echo "✅ lsof: 已安装"
    else
        echo "⚠️  lsof: 未安装 (可选)"
    fi
    
    echo ""
    
    # 如果有缺失依赖，提供安装提示
    if [ ${#missing_deps[@]} -gt 0 ]; then
        echo "❌ 缺少必要的系统依赖！"
        echo ""
        echo "📋 缺失的依赖: ${missing_deps[*]}"
        echo ""
        echo "💡 安装命令:"
        
        if [ "$OS_TYPE" = "Linux" ]; then
            if [[ "$OS_DISTRO" == *"Ubuntu"* ]] || [[ "$OS_DISTRO" == *"Debian"* ]]; then
                echo ""
                echo "  sudo apt update"
                echo "  sudo apt install -y ${missing_deps[*]}"
            elif [[ "$OS_DISTRO" == *"CentOS"* ]] || [[ "$OS_DISTRO" == *"Red Hat"* ]]; then
                echo ""
                echo "  sudo yum install -y ${missing_deps[*]}"
            else
                echo ""
                echo "  请使用系统的包管理器安装: ${missing_deps[*]}"
            fi
        elif [ "$OS_TYPE" = "macOS" ]; then
            echo ""
            echo "  brew install ${missing_deps[*]}"
        fi
        
        echo ""
        read -p "是否现在安装? (y/n): " install_deps
        
        if [ "$install_deps" = "y" ] || [ "$install_deps" = "Y" ]; then
            install_system_dependencies
        else
            echo ""
            echo "❌ 请先安装必要的依赖后再继续"
            echo ""
            read -p "按Enter键继续..."
            return 1
        fi
    else
        echo "✅ 所有必要的系统依赖已安装"
        echo ""
    fi
}

# 安装系统依赖
install_system_dependencies() {
    echo ""
    echo "正在安装系统依赖..."
    echo ""
    
    if [ "$OS_TYPE" = "Linux" ]; then
        if [[ "$OS_DISTRO" == *"Ubuntu"* ]] || [[ "$OS_DISTRO" == *"Debian"* ]]; then
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv git curl
        elif [[ "$OS_DISTRO" == *"CentOS"* ]] || [[ "$OS_DISTRO" == *"Red Hat"* ]]; then
            sudo yum install -y python3 python3-pip git curl
        fi
    elif [ "$OS_TYPE" = "macOS" ]; then
        if command -v brew &> /dev/null; then
            brew install python3 git curl
        else
            echo "❌ 未安装 Homebrew，请先安装: https://brew.sh/"
            return 1
        fi
    fi
    
    echo ""
    echo "✅ 系统依赖安装完成"
    echo ""
}

# 创建虚拟环境
create_virtual_environments() {
    echo "[2/6] 创建 Python 虚拟环境..."
    echo ""
    
    cd ~/trans_web_app || { echo "❌ 目录不存在: ~/trans_web_app"; return 1; }
    
    # OCR 服务
    echo "📦 创建 OCR 虚拟环境..."
    cd ocr
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ ocr/venv 已创建"
    else
        echo "⚠️  ocr/venv 已存在，跳过"
    fi
    cd ..
    
    # Inpaint 服务
    echo "📦 创建 Inpaint 虚拟环境..."
    cd inpaint
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ inpaint/venv 已创建"
    else
        echo "⚠️  inpaint/venv 已存在，跳过"
    fi
    cd ..
    
    # API 服务
    echo "📦 创建 API 虚拟环境..."
    cd translator_api
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ translator_api/venv 已创建"
    else
        echo "⚠️  translator_api/venv 已存在，跳过"
    fi
    cd ..
    
    echo ""
    echo "✅ 虚拟环境创建完成"
    echo ""
}

# 安装 Python 依赖包
install_python_packages() {
    echo "[3/6] 安装 Python 依赖包..."
    echo ""
    
    cd ~/trans_web_app || return 1
    
    # 安装 OCR 依赖
    echo "📦 安装 OCR 依赖..."
    cd ocr
    if [ -f "requirements.txt" ]; then
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        echo "✅ OCR 依赖安装完成"
    else
        echo "⚠️  ocr/requirements.txt 不存在"
    fi
    cd ..
    echo ""
    
    # 安装 Inpaint 依赖
    echo "📦 安装 Inpaint 依赖..."
    cd inpaint
    if [ -f "requirements.txt" ]; then
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        echo "✅ Inpaint 依赖安装完成"
    else
        echo "⚠️  inpaint/requirements.txt 不存在"
    fi
    cd ..
    echo ""
    
    # 安装 API 依赖
    echo "📦 安装 API 依赖..."
    cd translator_api
    if [ -f "requirements.txt" ]; then
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        echo "✅ API 依赖安装完成"
    else
        echo "⚠️  translator_api/requirements.txt 不存在"
    fi
    cd ..
    echo ""
    
    echo "✅ 所有 Python 依赖安装完成"
    echo ""
}

# 下载 AI 模型
download_models() {
    echo "[4/6] 下载 AI 模型..."
    echo ""
    
    echo "💡 提示: 模型文件较大，将自动从 Hugging Face 下载"
    echo "   如果下载失败，可以手动下载后放到 ~/.cache/huggingface/"
    echo ""
    
    read -p "是否现在下载模型? (y/n): " download_now
    
    if [ "$download_now" = "y" ] || [ "$download_now" = "Y" ]; then
        cd ~/trans_web_app/translator_api || return 1
        
        echo ""
        echo "📥 预下载翻译模型 (NLLB-200)..."
        source venv/bin/activate
        python3 << 'EOF'
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
print("正在下载 facebook/nllb-200-distilled-600M...")
try:
    tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    print("✅ 模型下载完成")
except Exception as e:
    print(f"❌ 模型下载失败: {e}")
EOF
        deactivate
        cd ~/trans_web_app
        echo ""
    else
        echo ""
        echo "⚠️  跳过模型下载，首次运行时会自动下载"
        echo ""
    fi
}

# 创建必要的目录
create_directories() {
    echo "[5/6] 创建必要的目录..."
    echo ""
    
    cd ~/trans_web_app || return 1
    
    # 创建日志目录
    if [ ! -d "logs" ]; then
        mkdir -p logs
        echo "✅ logs/ 目录已创建"
    else
        echo "⚠️  logs/ 目录已存在"
    fi
    
    # 创建上传目录
    if [ ! -d "translator_api/uploads" ]; then
        mkdir -p translator_api/uploads
        echo "✅ translator_api/uploads/ 目录已创建"
    else
        echo "⚠️  translator_api/uploads/ 目录已存在"
    fi
    
    # 创建输出目录
    if [ ! -d "translator_api/outputs" ]; then
        mkdir -p translator_api/outputs
        echo "✅ translator_api/outputs/ 目录已创建"
    else
        echo "⚠️  translator_api/outputs/ 目录已存在"
    fi
    
    echo ""
    echo "✅ 目录结构创建完成"
    echo ""
}

# 配置环境变量
setup_config_files() {
    echo "[6/6] 配置环境变量..."
    echo ""
    
    cd ~/trans_web_app || return 1
    
    # 创建 .env 示例文件
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# API 服务配置
API_BASE_URL=http://localhost:29003/api
APP_ENV=development
VERSION=3.0.0
APP_NAME=Image Translator

# 服务端口
OCR_PORT=29001
INPAINT_PORT=29002
API_PORT=29003
FRONTEND_PORT=5001

# 模型配置
TRANSLATION_MODEL=facebook/nllb-200-distilled-600M
OCR_MODEL=easyocr
INPAINT_MODEL=lama

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
EOF
        echo "✅ .env 文件已创建"
    else
        echo "⚠️  .env 文件已存在，跳过"
    fi
    
    echo ""
    echo "✅ 配置文件创建完成"
    echo ""
}

# ==========================================
# 原有功能保持不变
# ==========================================

start_services() {
    echo ""
    echo "正在启动所有服务 (后台模式)..."
    echo ""
    
    cd ~/trans_web_app
    
    # 创建日志目录
    if [ ! -d "logs" ]; then
        mkdir -p logs
        echo "✅ 已创建日志目录: logs/"
    fi
    
    # 🔥 启动 OCR 服务 - 强制使用 venv
    echo "[1/4] 启动 OCR 服务 (端口 29001)..."
    cd ~/trans_web_app/ocr
    if [ -d "venv" ]; then
        nohup bash -c "source venv/bin/activate && python app.py" > ../logs/ocr.log 2>&1 &
        OCR_PID=$!
        echo "✅ OCR服务已启动 (PID: $OCR_PID) [使用虚拟环境]"
    else
        echo "❌ 错误: venv 不存在，请先运行环境搭建 (菜单选项 9)"
        read -p "按Enter键继续..."
        return
    fi
    sleep 2
    
    # 🔥 启动 Inpaint 服务 - 强制使用 venv
    echo "[2/4] 启动 Inpaint 服务 (端口 29002)..."
    cd ~/trans_web_app/inpaint
    if [ -d "venv" ]; then
        nohup bash -c "source venv/bin/activate && python app.py" > ../logs/inpaint.log 2>&1 &
        INPAINT_PID=$!
        echo "✅ Inpaint服务已启动 (PID: $INPAINT_PID) [使用虚拟环境]"
    else
        echo "❌ 错误: venv 不存在，请先运行环境搭建 (菜单选项 9)"
        read -p "按Enter键继续..."
        return
    fi
    sleep 2
    
    # 🔥 启动 API 服务 - 强制使用 venv
    echo "[3/4] 启动 API 服务 (端口 29003)..."
    cd ~/trans_web_app/translator_api
    if [ -d "venv" ]; then
        nohup bash -c "source venv/bin/activate && python app.py" > ../logs/api.log 2>&1 &
        API_PID=$!
        echo "✅ API服务已启动 (PID: $API_PID) [使用虚拟环境]"
    else
        echo "❌ 错误: venv 不存在，请先运行环境搭建 (菜单选项 9)"
        read -p "按Enter键继续..."
        return
    fi
    sleep 2
    
    # 启动前端服务 (不需要 venv)
    echo "[4/4] 启动前端服务 (端口 5001)..."
    cd ~/trans_web_app/translator_frontend
    nohup python3 -m http.server 5001 > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
    
    cd ~/trans_web_app
    
    echo ""
    echo "========================================="
    echo "✅ 所有服务已在后台启动！"
    echo "========================================="
    echo ""
    echo "📋 日志文件:"
    echo "   tail -f logs/ocr.log"
    echo "   tail -f logs/inpaint.log"
    echo "   tail -f logs/api.log"
    echo "   tail -f logs/frontend.log"
    echo ""
    echo "📌 服务地址:"
    echo "   OCR服务:    http://localhost:29001"
    echo "   Inpaint服务: http://localhost:29002"
    echo "   API服务:    http://localhost:29003"
    echo "   前端界面:   http://localhost:5001"
    echo ""
    read -p "按Enter键继续..."
}

stop_services() {
    echo ""
    echo "正在停止所有服务..."
    echo ""
    
    # 统计停止的服务数量
    stopped_count=0
    
    # 停止 OCR 服务 (端口 29001)
    if lsof -Pi :29001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :29001 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ OCR服务已停止 (PID: $PID)"
            ((stopped_count++))
        else
            echo "⚠️  无法停止 OCR服务 (PID: $PID)"
        fi
    else
        echo "⚠️  OCR服务未运行"
    fi
    
    # 停止 Inpaint 服务 (端口 29002)
    if lsof -Pi :29002 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :29002 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Inpaint服务已停止 (PID: $PID)"
            ((stopped_count++))
        else
            echo "⚠️  无法停止 Inpaint服务 (PID: $PID)"
        fi
    else
        echo "⚠️  Inpaint服务未运行"
    fi
    
    # 停止 API 服务 (端口 29003)
    if lsof -Pi :29003 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :29003 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ API服务已停止 (PID: $PID)"
            ((stopped_count++))
        else
            echo "⚠️  无法停止 API服务 (PID: $PID)"
        fi
    else
        echo "⚠️  API服务未运行"
    fi
    
    # 停止前端服务 (端口 5001)
    if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :5001 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ 前端服务已停止 (PID: $PID)"
            ((stopped_count++))
        else
            echo "⚠️  无法停止前端服务 (PID: $PID)"
        fi
    else
        echo "⚠️  前端服务未运行"
    fi
    
    # 额外清理：强制杀死可能残留的进程
    pkill -f "python.*ocr/app.py" 2>/dev/null
    pkill -f "python.*inpaint/app.py" 2>/dev/null
    pkill -f "python.*translator_api/app.py" 2>/dev/null
    pkill -f "python.*http.server 5001" 2>/dev/null
    
    echo ""
    echo "========================================="
    if [ $stopped_count -gt 0 ]; then
        echo "✅ 已停止 $stopped_count 个服务"
    else
        echo "⚠️  没有运行中的服务"
    fi
    echo "========================================="
    echo ""
    read -p "按Enter键继续..."
}

restart_services() {
    echo ""
    echo "正在重启所有服务..."
    echo ""
    stop_services
    echo ""
    echo "等待 3 秒..."
    sleep 3
    echo ""
    start_services
}

check_status() {
    clear
    echo ""
    echo "========================================="
    echo "  服务状态"
    echo "========================================="
    echo ""
    
    # 检查端口函数
    check_port() {
        if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
            PID=$(lsof -Pi :$1 -sTCP:LISTEN -t)
            # 获取进程启动时间
            START_TIME=$(ps -p $PID -o lstart= 2>/dev/null || echo "未知")
            # 获取内存使用
            MEM=$(ps -p $PID -o rss= 2>/dev/null || echo "0")
            MEM_MB=$((MEM / 1024))
            echo "✅ $2 (端口 $1)"
            echo "   PID: $PID | 内存: ${MEM_MB}MB | 启动: $START_TIME"
        else
            echo "❌ $2 (端口 $1): 未运行"
        fi
        echo ""
    }
    
    check_port 29001 "OCR服务"
    check_port 29002 "Inpaint服务"
    check_port 29003 "API服务"
    check_port 5001 "前端服务"
    
    echo "========================================="
    echo ""
    read -p "按Enter键继续..."
}

view_logs() {
    cd ~/trans_web_app
    clear
    echo ""
    echo "========================================="
    echo "  查看日志文件"
    echo "========================================="
    echo ""
    
    # 检查logs目录是否存在
    if [ ! -d "logs" ]; then
        echo "❌ 日志目录不存在！"
        echo ""
        echo "💡 提示: 请先启动服务"
        echo ""
        read -p "按Enter键继续..."
        return
    fi
    
    echo "📋 当前日志文件:"
    echo ""
    
    # 显示日志文件信息
    if [ -f "logs/ocr.log" ]; then
        SIZE=$(du -h logs/ocr.log | cut -f1)
        LINES=$(wc -l < logs/ocr.log)
        echo "✅ logs/ocr.log       ($SIZE, $LINES 行)"
    else
        echo "❌ logs/ocr.log       (不存在)"
    fi
    
    if [ -f "logs/inpaint.log" ]; then
        SIZE=$(du -h logs/inpaint.log | cut -f1)
        LINES=$(wc -l < logs/inpaint.log)
        echo "✅ logs/inpaint.log   ($SIZE, $LINES 行)"
    else
        echo "❌ logs/inpaint.log   (不存在)"
    fi
    
    if [ -f "logs/api.log" ]; then
        SIZE=$(du -h logs/api.log | cut -f1)
        LINES=$(wc -l < logs/api.log)
        echo "✅ logs/api.log       ($SIZE, $LINES 行)"
    else
        echo "❌ logs/api.log       (不存在)"
    fi
    
    if [ -f "logs/frontend.log" ]; then
        SIZE=$(du -h logs/frontend.log | cut -f1)
        LINES=$(wc -l < logs/frontend.log)
        echo "✅ logs/frontend.log  ($SIZE, $LINES 行)"
    else
        echo "❌ logs/frontend.log  (不存在)"
    fi
    
    echo ""
    echo "========================================="
    echo ""
    echo "选择要查看的日志:"
    echo "  1. OCR服务 (最后50行)"
    echo "  2. Inpaint服务 (最后50行)"
    echo "  3. API服务 (最后50行)"
    echo "  4. 前端服务 (最后50行)"
    echo "  5. 返回主菜单"
    echo ""
    read -p "请选择 (1-5): " log_choice
    
    case $log_choice in
        1)
            if [ -f "logs/ocr.log" ]; then
                clear
                echo "========== OCR服务日志 (最后50行) =========="
                echo ""
                tail -n 50 logs/ocr.log
                echo ""
            else
                echo ""
                echo "❌ 日志文件不存在: logs/ocr.log"
                echo ""
            fi
            read -p "按Enter键继续..."
            view_logs
            ;;
        2)
            if [ -f "logs/inpaint.log" ]; then
                clear
                echo "========== Inpaint服务日志 (最后50行) =========="
                echo ""
                tail -n 50 logs/inpaint.log
                echo ""
            else
                echo ""
                echo "❌ 日志文件不存在: logs/inpaint.log"
                echo ""
            fi
            read -p "按Enter键继续..."
            view_logs
            ;;
        3)
            if [ -f "logs/api.log" ]; then
                clear
                echo "========== API服务日志 (最后50行) =========="
                echo ""
                tail -n 50 logs/api.log
                echo ""
            else
                echo ""
                echo "❌ 日志文件不存在: logs/api.log"
                echo ""
            fi
            read -p "按Enter键继续..."
            view_logs
            ;;
        4)
            if [ -f "logs/frontend.log" ]; then
                clear
                echo "========== 前端服务日志 (最后50行) =========="
                echo ""
                tail -n 50 logs/frontend.log
                echo ""
            else
                echo ""
                echo "❌ 日志文件不存在: logs/frontend.log"
                echo ""
            fi
            read -p "按Enter键继续..."
            view_logs
            ;;
        5)
            return
            ;;
        *)
            echo ""
            echo "❌ 无效选择！"
            sleep 1
            view_logs
            ;;
    esac
}

tail_logs() {
    cd ~/trans_web_app
    clear
    echo ""
    echo "========================================="
    echo "  实时查看日志 (Ctrl+C 退出)"
    echo "========================================="
    echo ""
    
    if [ ! -d "logs" ]; then
        echo "❌ 日志目录不存在！"
        echo ""
        read -p "按Enter键继续..."
        return
    fi
    
    echo "选择要实时查看的日志:"
    echo "  1. OCR服务"
    echo "  2. Inpaint服务"
    echo "  3. API服务"
    echo "  4. 前端服务"
    echo "  5. 所有服务"
    echo "  6. 返回主菜单"
    echo ""
    read -p "请选择 (1-6): " tail_choice
    
    case $tail_choice in
        1)
            if [ -f "logs/ocr.log" ]; then
                echo ""
                echo "实时查看 OCR 服务日志 (Ctrl+C 退出)..."
                echo ""
                tail -f logs/ocr.log
            else
                echo "❌ 日志文件不存在"
            fi
            ;;
        2)
            if [ -f "logs/inpaint.log" ]; then
                echo ""
                echo "实时查看 Inpaint 服务日志 (Ctrl+C 退出)..."
                echo ""
                tail -f logs/inpaint.log
            else
                echo "❌ 日志文件不存在"
            fi
            ;;
        3)
            if [ -f "logs/api.log" ]; then
                echo ""
                echo "实时查看 API 服务日志 (Ctrl+C 退出)..."
                echo ""
                tail -f logs/api.log
            else
                echo "❌ 日志文件不存在"
            fi
            ;;
        4)
            if [ -f "logs/frontend.log" ]; then
                echo ""
                echo "实时查看前端服务日志 (Ctrl+C 退出)..."
                echo ""
                tail -f logs/frontend.log
            else
                echo "❌ 日志文件不存在"
            fi
            ;;
        5)
            echo ""
            echo "实时查看所有服务日志 (Ctrl+C 退出)..."
            echo ""
            tail -f logs/*.log
            ;;
        6)
            return
            ;;
        *)
            echo "❌ 无效选择！"
            sleep 1
            tail_logs
            ;;
    esac
}

health_check() {
    clear
    echo ""
    echo "========================================="
    echo "  健康检查"
    echo "========================================="
    echo ""
    
    check_service() {
        echo -n "检查 $2..."
        if timeout 5 curl -s -f $1 > /dev/null 2>&1; then
            echo " ✅ 正常"
            return 0
        else
            echo " ❌ 异常或未运行"
            return 1
        fi
    }
    
    success_count=0
    total_count=4
    
    check_service "http://localhost:29001/health" "OCR服务 (29001)" && ((success_count++))
    check_service "http://localhost:29002/health" "Inpaint服务 (29002)" && ((success_count++))
    check_service "http://localhost:29003/api/health" "API服务 (29003)" && ((success_count++))
    check_service "http://localhost:5001" "前端服务 (5001)" && ((success_count++))
    
    echo ""
    echo "========================================="
    echo "结果: $success_count/$total_count 服务正常"
    echo "========================================="
    echo ""
    read -p "按Enter键继续..."
}

clean_logs() {
    echo ""
    echo "⚠️  警告: 这将删除所有日志文件！"
    echo ""
    read -p "确认继续? (y/n): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        cd ~/trans_web_app
        if [ -d "logs" ]; then
            rm -f logs/*.log
            echo ""
            echo "✅ 日志文件已清理！"
        else
            echo ""
            echo "⚠️  日志目录不存在"
        fi
    else
        echo ""
        echo "❌ 已取消操作"
    fi
    echo ""
    read -p "按Enter键继续..."
}

# 主循环
while true; do
    show_menu
    read choice
    
    case $choice in
        1) start_services ;;
        2) stop_services ;;
        3) restart_services ;;
        4) check_status ;;
        5) view_logs ;;
        6) tail_logs ;;
        7) health_check ;;
        8) clean_logs ;;
        9) setup_environment ;;
        10) restart_single_service ;;
        0) 
            clear
            echo ""
            echo "👋 再见！"
            echo ""
            exit 0
            ;;
        *) 
            echo ""
            echo "❌ 无效选择！"
            sleep 1
            ;;
    esac
done
# === 重启单个服务功能 ===
restart_single_service() {
    clear
    echo ""
    echo "========================================="
    echo "  重启单个服务"
    echo "========================================="
    echo ""
    echo "请选择要重启的服务:"
    echo "  1. OCR服务"
    echo "  2. Inpaint服务"
    echo "  3. API服务"
    echo "  4. 前端服务"
    echo "  5. 返回主菜单"
    echo ""
    read -p "请选择 (1-5): " svc_choice

    case $svc_choice in
        1)
            stop_ocr_service
            start_ocr_service
            ;;
        2)
            stop_inpaint_service
            start_inpaint_service
            ;;
        3)
            stop_api_service
            start_api_service
            ;;
        4)
            stop_frontend_service
            start_frontend_service
            ;;
        5)
            return
            ;;
        *)
            echo "❌ 无效选择！"
            sleep 1
            ;;
    esac
    echo ""
    read -p "按Enter键继续..."
}

stop_ocr_service() {
    if lsof -Pi :29001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :29001 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        echo "✅ OCR服务已停止 (PID: $PID)"
    else
        echo "⚠️  OCR服务未运行"
    fi
}
start_ocr_service() {
    cd ~/trans_web_app/ocr
    nohup bash -c "source venv/bin/activate && python app.py" > ../logs/ocr.log 2>&1 &
    echo "✅ OCR服务已启动"
    cd ~/trans_web_app
}

stop_inpaint_service() {
    if lsof -Pi :29002 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :29002 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        echo "✅ Inpaint服务已停止 (PID: $PID)"
    else
        echo "⚠️  Inpaint服务未运行"
    fi
}
start_inpaint_service() {
    cd ~/trans_web_app/inpaint
    nohup bash -c "source venv/bin/activate && python app.py" > ../logs/inpaint.log 2>&1 &
    echo "✅ Inpaint服务已启动"
    cd ~/trans_web_app
}

stop_api_service() {
    if lsof -Pi :29003 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :29003 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        echo "✅ API服务已停止 (PID: $PID)"
    else
        echo "⚠️  API服务未运行"
    fi
}

start_api_service() {
    cd ~/trans_web_app/translator_api
    # 🔥 使用 PYTHONPATH 和 cd 确保路径正确
    nohup bash -c "
        cd ~/trans_web_app/translator_api
        export PYTHONPATH=~/trans_web_app/translator_api:\$PYTHONPATH
        source venv/bin/activate
        python app.py
    " > ../logs/api.log 2>&1 &
    echo "✅ API服务已启动"
    cd ~/trans_web_app
}

stop_frontend_service() {
    if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        PID=$(lsof -Pi :5001 -sTCP:LISTEN -t)
        kill $PID 2>/dev/null
        echo "✅ 前端服务已停止 (PID: $PID)"
    else
        echo "⚠️  前端服务未运行"
    fi
}
start_frontend_service() {
    cd ~/trans_web_app/translator_frontend
    nohup python3 -m http.server 5001 > ../logs/frontend.log 2>&1 &
    echo "✅ 前端服务已启动"
    cd ~/trans_web_app
}