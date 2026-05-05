#!/bin/bash

echo "=== Flask 服务器重启脚本 ==="
echo ""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/dingtalk-app.log"

# 查找正在运行的 Flask 进程
FLASK_PID=$(ps aux | grep "python.*run.py" | grep -v grep | grep -v "bash -O" | awk '{print $2}')

if [ -z "$FLASK_PID" ]; then
    echo "❌ 未找到正在运行的 Flask 服务器"
    echo ""
    echo "启动服务器："
    cd "$SCRIPT_DIR"
    nohup python3 run.py > "$LOG_FILE" 2>&1 &
    echo "✅ 服务器已启动，PID: $!"
    echo "日志文件: $LOG_FILE"
else
    echo "找到 Flask 服务器进程："
    ps aux | grep "python.*run.py" | grep -v grep | grep -v "bash -O"
    echo ""
    
    echo "停止服务器..."
    kill $FLASK_PID
    sleep 2
    
    # 检查是否还在运行
    if ps -p $FLASK_PID > /dev/null 2>&1; then
        echo "强制停止..."
        kill -9 $FLASK_PID
        sleep 1
    fi
    
    echo "✅ 服务器已停止"
    echo ""
    
    echo "启动服务器..."
    cd "$SCRIPT_DIR"
    nohup python3 run.py > "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    sleep 2
    
    echo "✅ 服务器已重启"
    echo "新的 PID: $NEW_PID"
    echo "日志文件: $LOG_FILE"
fi

echo ""
echo "查看日志："
echo "  tail -f $LOG_FILE"
echo ""
echo "检查服务器状态："
echo "  ps aux | grep 'python.*run.py' | grep -v grep"
echo ""
echo "=== 重启完成 ==="
