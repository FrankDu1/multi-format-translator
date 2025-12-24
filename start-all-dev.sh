#!/bin/bash
# filepath: /path/to/trans_web_app/start-all-dev.sh

echo "========================================="
echo "  启动所有翻译服务 (开发模式)"
echo "========================================="
echo ""

# 检查 tmux 是否安装
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux 未安装，正在安装..."
    sudo apt-get update && sudo apt-get install -y tmux
fi

# 创建新的 tmux 会话
SESSION_NAME="translator-services"

# 如果会话已存在，先关闭
tmux kill-session -t $SESSION_NAME 2>/dev/null

# 创建新会话并启动第一个服务 (OCR)
tmux new-session -d -s $SESSION_NAME -n "ocr" "cd ~/trans_web_app/ocr && python3 app.py"

# 创建新窗口并启动其他服务
tmux new-window -t $SESSION_NAME -n "inpaint" "cd ~/trans_web_app/inpaint && python3 app.py"
tmux new-window -t $SESSION_NAME -n "api" "cd ~/trans_web_app/translator_api && python3 app.py"
tmux new-window -t $SESSION_NAME -n "frontend" "cd ~/trans_web_app/translator_frontend && python3 -m http.server 5001"

echo ""
echo "✅ 所有服务已启动！"
echo ""
echo "📌 服务地址:"
echo "   OCR服务:    http://localhost:29001"
echo "   Inpaint服务: http://localhost:29002"
echo "   API服务:    http://localhost:29003"
echo "   前端界面:   http://localhost:5001"
echo ""
echo "🔍 查看服务:"
echo "   tmux attach -t $SESSION_NAME    # 进入会话"
echo "   Ctrl+B 然后按数字键 0-3         # 切换窗口"
echo "   Ctrl+B 然后按 D                # 退出会话(服务继续运行)"
echo ""
echo "🛑 停止所有服务:"
echo "   ./stop-all-dev.sh"
echo ""