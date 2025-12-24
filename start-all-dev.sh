#!/bin/bash
# 启动所有翻译服务 (开发模式)

echo "========================================="
echo "  启动所有翻译服务 (开发模式)"
echo "========================================="
echo ""

# 加载环境变量
if [ -f .env ]; then
    echo "📝 加载环境变量..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# 设置默认值
export API_HOST=${API_HOST:-0.0.0.0}
export API_PORT=${API_PORT:-5002}
export OCR_HOST=${OCR_HOST:-0.0.0.0}
export OCR_PORT=${OCR_PORT:-8899}
export INPAINT_HOST=${INPAINT_HOST:-0.0.0.0}
export INPAINT_PORT=${INPAINT_PORT:-8900}
export FRONTEND_PORT=${FRONTEND_PORT:-5001}

# 检查 tmux 是否安装
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux 未安装，正在安装..."
    sudo apt-get update && sudo apt-get install -y tmux
fi

# 创建新的 tmux 会话
SESSION_NAME="translator-services"

# 如果会话已存在，先关闭
tmux kill-session -t $SESSION_NAME 2>/dev/null

# 获取当前目录
CURRENT_DIR=$(pwd)

# 创建新会话并启动第一个服务 (OCR)
tmux new-session -d -s $SESSION_NAME -n "ocr" "cd $CURRENT_DIR/ocr && python3 app.py"

# 创建新窗口并启动其他服务
tmux new-window -t $SESSION_NAME -n "inpaint" "cd $CURRENT_DIR/inpaint && python3 app.py"
tmux new-window -t $SESSION_NAME -n "api" "cd $CURRENT_DIR/translator_api && python3 app.py"
tmux new-window -t $SESSION_NAME -n "frontend" "cd $CURRENT_DIR/translator_frontend && python3 -m http.server $FRONTEND_PORT"

echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "📌 服务地址:"
echo "   OCR服务:    http://localhost:$OCR_PORT"
echo "   Inpaint服务: http://localhost:$INPAINT_PORT"
echo "   API服务:    http://localhost:$API_PORT"
echo "   前端界面:   http://localhost:$FRONTEND_PORT"
echo ""
echo "🔍 查看服务:"
echo "   tmux attach -t $SESSION_NAME    # 进入会话"
echo "   Ctrl+B 然后按数字键 0-3         # 切换窗口"
echo "   Ctrl+B 然后按 D                # 退出会话(服务继续运行)"
echo ""
echo "🛑 停止所有服务:"
echo "   ./stop-all-dev.sh"
echo ""