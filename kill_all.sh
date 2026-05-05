#!/bin/bash

# kill_all.sh - 停止本项目的所有服务（Flask + Vite）

echo "=========================================="
echo "🛑 停止所有服务（Flask + Vite）"
echo "=========================================="
echo ""

# 统计
STOPPED_COUNT=0

# 停止 Flask（5000 端口）
echo "📍 处理 Flask 后端（端口 5000）..."
PIDS=$(lsof -i :5000 | grep LISTEN | awk '{print $2}')

if [ -n "$PIDS" ]; then
    for PID in $PIDS; do
        echo "   ⏹️  停止 PID: $PID"
        kill -9 $PID 2>/dev/null
        ((STOPPED_COUNT++))
    done
    sleep 1
    
    if lsof -i :5000 > /dev/null 2>&1; then
        echo "   ⚠️  端口 5000 仍在使用中"
    else
        echo "   ✅ Flask 已停止"
    fi
else
    echo "   ℹ️  未找到 Flask 进程"
fi

echo ""

# 停止 Vite（5173 端口）
echo "📍 处理 Vite 前端（端口 5173）..."
PIDS=$(lsof -i :5173 | grep LISTEN | awk '{print $2}')

if [ -n "$PIDS" ]; then
    for PID in $PIDS; do
        echo "   ⏹️  停止 PID: $PID"
        kill -9 $PID 2>/dev/null
        ((STOPPED_COUNT++))
    done
    sleep 1
    
    if lsof -i :5173 > /dev/null 2>&1; then
        echo "   ⚠️  端口 5173 仍在使用中"
    else
        echo "   ✅ Vite 已停止"
    fi
else
    echo "   ℹ️  未找到 Vite 进程"
fi

echo ""
echo "=========================================="
echo "✅ 完成：停止了 $STOPPED_COUNT 个进程"
echo "=========================================="
echo ""

# 显示当前开放的端口
echo "📊 当前监听的主要端口："
lsof -i -P | grep LISTEN | awk '{print $9}' | sort | uniq

echo ""
