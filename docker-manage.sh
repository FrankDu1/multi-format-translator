#!/bin/bash

# Docker部署管理脚本 - 多格式翻译工具
# 用法: ./docker-manage.sh [命令]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo ""
    echo "========================================"
    echo "  $1"
    echo "========================================"
    echo ""
}

# 检查Docker环境
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "未检测到Docker，请先安装Docker"
        echo "安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "未检测到docker-compose"
        exit 1
    fi

    print_success "Docker环境正常"
}

# 检查配置文件
check_config() {
    if [ ! -f ".env" ]; then
        print_warning "未找到 .env 文件"
        if [ -f ".env.example" ]; then
            print_info "从 .env.example 创建 .env..."
            cp .env.example .env
            print_success "已创建 .env 文件"
        else
            print_warning "使用默认配置"
        fi
    else
        print_success "配置文件存在"
    fi
}

# 启动所有服务
start_all() {
    print_header "🚀 一键启动所有服务"
    
    check_docker
    check_config
    
    echo "开始构建并启动服务..."
    echo "第一次运行可能需要10-15分钟下载依赖"
    echo ""
    
    docker-compose up -d --build
    
    if [ $? -eq 0 ]; then
        print_header "✅ 所有服务启动成功！"
        echo "服务地址:"
        echo "  前端界面: http://localhost:5001"
        echo "  API服务:  http://localhost:5002"
        echo "  OCR服务:  http://localhost:8899"
        echo "  Inpaint:  http://localhost:8900"
        echo ""
        print_info "等待1-2分钟让服务完全启动"
    else
        print_error "启动失败！请检查错误信息"
        exit 1
    fi
}

# 仅构建
build_only() {
    print_header "📦 构建Docker镜像"
    check_docker
    docker-compose build
    print_success "构建完成"
}

# 仅启动
start_only() {
    print_header "▶️  启动服务"
    docker-compose up -d
    print_success "启动成功"
    echo "访问地址: http://localhost:5001"
}

# 停止服务
stop_services() {
    print_header "⏸️  停止所有服务"
    docker-compose down
    print_success "所有服务已停止"
}

# 重启服务
restart_services() {
    print_header "🔄 重启所有服务"
    docker-compose restart
    print_success "所有服务已重启"
}

# 查看状态
show_status() {
    print_header "📊 服务状态"
    docker-compose ps
    echo ""
    echo "========================================"
    echo "  容器资源使用情况"
    echo "========================================"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
        translator-frontend translator-api translator-ocr translator-inpaint 2>/dev/null || true
}

# 查看日志
show_logs() {
    print_header "📝 实时日志"
    print_info "按 Ctrl+C 退出日志查看"
    sleep 1
    docker-compose logs -f --tail=100
}

# 清理
clean() {
    print_header "🧹 清理停止的容器"
    docker-compose down
    print_success "清理完成"
}

# 完全清理
clean_all() {
    print_header "🗑️  完全清理"
    print_warning "这将删除所有容器、镜像和数据卷"
    read -p "确定要继续吗？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v
        docker system prune -f
        print_success "清理完成"
    else
        print_info "已取消"
    fi
}

# 重新构建
rebuild() {
    print_header "🔧 重新构建并启动"
    
    echo "停止现有服务..."
    docker-compose down
    
    echo "重新构建镜像..."
    docker-compose build --no-cache
    
    echo "启动服务..."
    docker-compose up -d
    
    print_success "重建成功"
    echo "访问地址: http://localhost:5001"
}

# 显示帮助
show_help() {
    echo "Docker部署管理脚本 - 多格式翻译工具"
    echo ""
    echo "用法: ./docker-manage.sh [命令]"
    echo ""
    echo "命令:"
    echo "  start       - 一键启动所有服务（构建+运行）"
    echo "  build       - 仅构建镜像"
    echo "  up          - 启动已构建的服务"
    echo "  stop        - 停止所有服务"
    echo "  restart     - 重启所有服务"
    echo "  status      - 查看服务状态"
    echo "  logs        - 查看实时日志"
    echo "  clean       - 清理停止的容器"
    echo "  clean-all   - 完全清理（包括数据卷）"
    echo "  rebuild     - 重新构建并启动"
    echo "  help        - 显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./docker-manage.sh start      # 启动所有服务"
    echo "  ./docker-manage.sh logs       # 查看日志"
    echo "  ./docker-manage.sh stop       # 停止服务"
}

# 交互式菜单
show_menu() {
    while true; do
        clear
        print_header "Docker部署管理 - 翻译服务"
        
        echo "当前状态:"
        docker-compose ps 2>/dev/null || echo "服务未运行"
        
        echo ""
        echo "========================================"
        echo "  请选择操作:"
        echo "========================================"
        echo ""
        echo " [1] 🚀 一键启动所有服务（构建+运行）"
        echo " [2] 📦 仅构建镜像"
        echo " [3] ▶️  启动已构建的服务"
        echo " [4] ⏸️  停止所有服务"
        echo " [5] 🔄 重启所有服务"
        echo " [6] 📊 查看服务状态"
        echo " [7] 📝 查看实时日志"
        echo " [8] 🧹 清理停止的服务"
        echo " [9] 🗑️  完全清理（包括数据卷）"
        echo "[10] 🔧 重新构建并启动"
        echo " [0] ❌ 退出"
        echo ""
        echo "========================================"
        read -p "请输入选项 (0-10): " choice
        
        case $choice in
            1) start_all; read -p "按Enter继续..." ;;
            2) build_only; read -p "按Enter继续..." ;;
            3) start_only; read -p "按Enter继续..." ;;
            4) stop_services; read -p "按Enter继续..." ;;
            5) restart_services; read -p "按Enter继续..." ;;
            6) show_status; read -p "按Enter继续..." ;;
            7) show_logs ;;
            8) clean; read -p "按Enter继续..." ;;
            9) clean_all; read -p "按Enter继续..." ;;
            10) rebuild; read -p "按Enter继续..." ;;
            0) echo "感谢使用！"; exit 0 ;;
            *) print_error "无效选项"; sleep 1 ;;
        esac
    done
}

# 主函数
main() {
    case "${1:-}" in
        start)
            start_all
            ;;
        build)
            build_only
            ;;
        up)
            start_only
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        clean)
            clean
            ;;
        clean-all)
            clean_all
            ;;
        rebuild)
            rebuild
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            # 无参数时显示交互式菜单
            show_menu
            ;;
        *)
            print_error "未知命令: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
