#!/bin/bash

# kill_flask.sh - 停止 Flask 后端服务（默认端口 5000）
# 用法：./kill_flask.sh [port]
# 例如：./kill_flask.sh 5000

PORT=${1:-5000}

echo "🔍 查找在 $PORT 端口上的进程..."
echo ""

# 方法 1：查找在指定端口上的进程（包括所有类型）
PIDS=$(lsof -i :$PORT -t 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "❌ 未找到在 $PORT 端口上运行的进程"
    echo ""
    echo "💡 提示："
    echo "   - 检查 Flask 是否已启动"
    echo "   - 使用 'lsof -i :$PORT' 查看该端口占用情况"
    echo "   - 或尝试使用 'ps aux | grep python' 查看 Python 进程"
    exit 0
fi

echo "✅ 找到以下进程占用 $PORT 端口："
lsof -i :$PORT

echo ""
echo "⏹️  正在停止这些进程..."

for PID in $PIDS; do
    COMMAND=$(ps -p $PID -o comm= 2>/dev/null)
    echo "   停止 $COMMAND (PID: $PID)"
    kill -9 $PID 2>/dev/null
done

sleep 2

# 验证进程是否已停止
REMAINING=$(lsof -i :$PORT -t 2>/dev/null)
if [ -n "$REMAINING" ]; then
    echo ""
    echo "⚠️  警告：$PORT 端口仍在使用中，显示详情："
    lsof -i :$PORT
    echo ""
    echo "💡 这可能是 macOS 系统进程（如 ControlCenter）"
    echo "   可以尝试以下方法："
    echo "   1. 重启 macOS"
    echo "   2. 改用其他端口运行 Flask：python run.py --port 5001"
    echo "   3. 查看进程详情：ps aux | grep $(lsof -i :$PORT -t | head -1)"
else
    echo "✅ 成功停止 $PORT 端口的所有进程"
fi

echo ""
