#!/bin/bash
# filepath: /path/to/trans_web_app/stop-all-dev.sh

echo "正在停止所有服务..."

SESSION_NAME="translator-services"
tmux kill-session -t $SESSION_NAME 2>/dev/null

echo "✅ 所有服务已停止！"