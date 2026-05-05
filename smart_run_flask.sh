#!/bin/bash

# smart_run_flask.sh - 智能启动 Flask，自动找可用端口

echo "════════════════════════════════════════════════════════════════"
echo "🚀 Flask 智能启动脚本"
echo "════════════════════════════════════════════════════════════════"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 激活虚拟环境
if [ -d "$SCRIPT_DIR/dingvenv" ]; then
    echo "✓ 激活虚拟环境..."
    source "$SCRIPT_DIR/dingvenv/bin/activate"
else
    echo "❌ 未找到虚拟环境 dingvenv"
    exit 1
fi

echo ""

# 尝试查找可用端口
PREFERRED_PORTS=(5000 5001 5002 5003 5004 5005 5010 5020 8000 8080)
AVAILABLE_PORT=""

echo "🔍 查找可用端口..."
for PORT in "${PREFERRED_PORTS[@]}"; do
    if ! lsof -i :$PORT > /dev/null 2>&1; then
        echo "✅ 端口 $PORT 可用"
        AVAILABLE_PORT=$PORT
        break
    else
        PROC_INFO=$(lsof -i :$PORT | tail -1)
        echo "❌ 端口 $PORT 被占用：$PROC_INFO"
    fi
done

echo ""

if [ -z "$AVAILABLE_PORT" ]; then
    echo "⚠️  未能找到可用端口，将尝试使用端口 5000"
    echo "   如果失败，请手动指定端口"
    AVAILABLE_PORT=5000
fi

echo "════════════════════════════════════════════════════════════════"
echo "🎯 将在端口 $AVAILABLE_PORT 启动 Flask"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "📍 应用地址："
echo "   http://localhost:$AVAILABLE_PORT"
echo "   http://127.0.0.1:$AVAILABLE_PORT"
echo ""
echo "⏹️  停止应用：按 Ctrl+C"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 启动 Flask
cd "$SCRIPT_DIR"
export FLASK_PORT=$AVAILABLE_PORT
python run.py
