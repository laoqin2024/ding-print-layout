#!/bin/bash

# kill_vite.sh - 停止 Vite 前端开发服务（端口 5173）

echo "🔍 查找 Vite 进程..."
echo ""

# 方法 1：查找在 5173 端口上的进程
PIDS=$(lsof -i :5173 | grep LISTEN | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "❌ 未找到在 5173 端口上运行的 Vite 进程"
    echo ""
    echo "💡 提示："
    echo "   - 检查 Vite 是否已启动"
    echo "   - 使用 'lsof -i :5173' 查看该端口占用情况"
    echo "   - 或使用: pkill -f vite"
    exit 0
fi

echo "✅ 找到以下 Vite 进程："
lsof -i :5173 | grep LISTEN

echo ""
echo "⏹️  正在停止 Vite..."

for PID in $PIDS; do
    echo "   停止 PID: $PID"
    kill -9 $PID 2>/dev/null
done

sleep 1

# 验证进程是否已停止
if lsof -i :5173 > /dev/null 2>&1; then
    echo "⚠️  警告：5173 端口仍在使用中"
    lsof -i :5173
else
    echo "✅ Vite 已成功停止（5173 端口已释放）"
fi

echo ""
