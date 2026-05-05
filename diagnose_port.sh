#!/bin/bash

# diagnose_port.sh - 诊断 5000 端口占用情况

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║        🔍 Flask 5000 端口诊断工具                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

PORT=5000

echo "📊 步骤 1：检查 $PORT 端口状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
lsof -i :$PORT || echo "✅ 端口未被占用"

echo ""
echo "📊 步骤 2：查找所有 Python 进程"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep python | grep -v grep || echo "✅ 未运行 Python 进程"

echo ""
echo "📊 步骤 3：查找 Flask 相关进程"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
ps aux | grep -E "run.py|flask|app.py" | grep -v grep || echo "✅ 未运行 Flask 进程"

echo ""
echo "📊 步骤 4：所有监听的端口"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "监听的所有端口（监听状态）："
lsof -i -P | grep LISTEN | awk '{print $9}' | sort | uniq

echo ""
echo "📊 步骤 5：识别 $PORT 端口的占用进程"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PIDS=$(lsof -i :$PORT -t 2>/dev/null)

if [ -z "$PIDS" ]; then
    echo "✅ 端口 $PORT 未被占用"
else
    echo "❌ 找到占用 $PORT 端口的进程："
    for PID in $PIDS; do
        echo ""
        echo "PID: $PID"
        ps -p $PID -o pid,user,comm,args
    done
fi

echo ""
echo "🔧 建议："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -z "$PIDS" ]; then
    echo "✅ 端口 $PORT 已可用，可以启动 Flask 应用"
    echo "   使用：python run.py"
else
    # 检查是否是 ControlCenter
    COMM=$(ps -p $(echo $PIDS | awk '{print $1}') -o comm= 2>/dev/null)
    if [[ "$COMM" == *"ControlCenter"* ]]; then
        echo "⚠️  发现 macOS ControlCenter 占用 $PORT 端口"
        echo ""
        echo "🔍 ControlCenter 是 macOS 系统应用，会自动重启"
        echo ""
        echo "💡 解决方案 1：改用其他端口"
        echo "   修改 run.py 或 app.py，改为使用其他端口，如 5001、5002 等"
        echo "   或在命令行指定端口："
        echo "   $ FLASK_PORT=5001 python run.py"
        echo ""
        echo "💡 解决方案 2：重启 macOS"
        echo "   重启后 ControlCenter 的端口占用通常会释放"
        echo ""
        echo "💡 解决方案 3：使用脚本强制停止（临时方案）"
        echo "   $ kill -9 $PIDS"
        echo "   注意：ControlCenter 会自动重启"
    else
        echo "⚠️  发现进程占用 $PORT 端口："
        echo "   进程名: $COMM (PID: $PIDS)"
        echo ""
        echo "💡 可以尝试以下命令停止："
        echo "   $ kill -9 $PIDS"
        echo ""
        echo "💡 或改用其他端口运行 Flask"
    fi
fi

echo ""
