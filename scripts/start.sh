#!/bin/bash

# ==========================================
# DingTalk Print Layout - 生产环境启动脚本
# ==========================================

# 获取脚本所在目录的上一级目录（即项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 准备启动服务..."

# 1. 修复由于跨机器/跨操作系统直接拷贝目录导致的 venv 路径和二进制失效问题
if [ -d "dingvenv" ]; then
    # 测试现有的 python 是否能正常运行（跨平台拷贝的通常会直接报错找不到文件或格式错误）
    if ! ./dingvenv/bin/python3 --version > /dev/null 2>&1; then
        echo "⚠️ 检测到虚拟环境已损坏或不兼容（跨机器拷贝所致），正在清理重建..."
        rm -rf dingvenv
    fi
fi

# 2. 如果没有虚拟环境，则创建一个干净的，并安装依赖
if [ ! -d "dingvenv" ]; then
    echo "🐍 创建全新的本地虚拟环境..."
    python3 -m venv dingvenv
    
    echo "📦 安装依赖库..."
    ./dingvenv/bin/python3 -m pip install --upgrade pip
    ./dingvenv/bin/python3 -m pip install -r requirements.txt
    
    # 生产环境推荐使用 gunicorn，确保已安装
    ./dingvenv/bin/python3 -m pip install gunicorn
fi

# 3. 创建必要的目录
mkdir -p data static/outputs templates/pdf_templates logs

# 4. 启动服务
echo "🟢 启动 Gunicorn Web 服务 (后台运行)..."

# 先杀掉可能残留的旧进程，防止端口被占用
pkill -f "gunicorn.*run:app" || true

# 使用 nohup 在后台启动，并将输出重定向到日志文件
nohup ./dingvenv/bin/gunicorn -w 4 -b 0.0.0.0:8000 run:app > logs/app.log 2>&1 &

echo "=========================================="
echo "✅ 服务已在后台成功启动！监听端口: 8000"
echo "📄 您可以随时使用以下命令查看运行日志："
echo "   tail -f logs/app.log"
echo "=========================================="
