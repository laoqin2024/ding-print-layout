#!/bin/bash

echo "=========================================="
echo "  设计器修复验证测试"
echo "=========================================="
echo ""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/dingtalk-app.log"

echo "✅ 服务器状态检查"
echo "----------------------------------------"
FLASK_PID=$(ps aux | grep "python.*run.py" | grep -v grep | grep -v "bash -O" | awk 'NR==1{print $2}')
if [ -n "$FLASK_PID" ]; then
    echo "✅ Flask 服务器正在运行"
    echo "   PID: $FLASK_PID"
    echo "   启动时间: $(ps -p $FLASK_PID -o lstart=)"
else
    echo "❌ Flask 服务器未运行"
    exit 1
fi
echo ""

echo "✅ 代码修改检查"
echo "----------------------------------------"

# 检查状态章 overlay
STAMP_OVERLAY=$(grep -c "stamp_path.*insert_image.*overlay=True" "$SCRIPT_DIR/app/routes/designer.py")
if [ "$STAMP_OVERLAY" -gt 0 ]; then
    echo "✅ 状态章 overlay=True 已添加"
else
    echo "❌ 状态章 overlay=True 未找到"
fi

# 检查签名 overlay
SIG_OVERLAY=$(grep -c "sig_fill_mode.*auto_sequence" "$SCRIPT_DIR/app/routes/designer.py" -A 10 | grep -c "overlay=True")
if [ "$SIG_OVERLAY" -gt 0 ]; then
    echo "✅ 签名 overlay=True 已添加"
else
    echo "❌ 签名 overlay=True 未找到"
fi

# 检查部门控件换行代码
DEPT_WRAP=$(grep -c "r === \"dept\"" "$SCRIPT_DIR/static/js/designer_edit.js" -A 5 | grep -c "whiteSpace.*normal")
if [ "$DEPT_WRAP" -gt 0 ]; then
    echo "✅ 部门控件换行代码已添加"
else
    echo "❌ 部门控件换行代码未找到"
fi

echo ""

echo "✅ PNG 文件检查"
echo "----------------------------------------"
for png in "$SCRIPT_DIR/static/stamps/client"/*.png; do
    if [ -f "$png" ]; then
        INFO=$(file "$png")
        if echo "$INFO" | grep -q "RGBA"; then
            echo "✅ $(basename $png) - 包含透明通道"
        else
            echo "⚠️  $(basename $png) - 不包含透明通道"
        fi
    fi
done
echo ""

echo "✅ 日志检查"
echo "----------------------------------------"
if [ -f "$LOG_FILE" ]; then
    echo "最近的日志（最后10行）："
    tail -10 "$LOG_FILE"
else
    echo "⚠️  日志文件不存在: $LOG_FILE"
fi
echo ""

echo "=========================================="
echo "  测试步骤"
echo "=========================================="
echo ""
echo "1. 在浏览器中强制刷新（Ctrl+Shift+R）"
echo ""
echo "2. 测试状态章透明背景："
echo "   - 打开设计器"
echo "   - 预览 PDF"
echo "   - 检查状态章是否透明"
echo ""
echo "3. 测试部门控件换行："
echo "   - 选中部门控件"
echo "   - 勾选'文本自动换行'"
echo "   - 点击'更新选中项'"
echo "   - 点击'保存布局'"
echo "   - 预览 PDF"
echo ""
echo "4. 在浏览器控制台运行调试代码："
echo "   const idx = Array.from(state.selected)[0];"
echo "   console.log('text_wrap:', state.items[idx].text_wrap);"
echo "   console.log('white-space:', window.getComputedStyle(document.querySelector(\`[data-idx=\"\${idx}\"]\`)).whiteSpace);"
echo ""
echo "=========================================="
echo "  预期结果"
echo "=========================================="
echo ""
echo "✅ 状态章："
echo "   - 透明背景"
echo "   - 可以看到底图内容"
echo "   - 没有白色背景"
echo ""
echo "✅ 部门控件："
echo "   - text_wrap: true"
echo "   - white-space: normal"
echo "   - 画布中文本换行"
echo "   - PDF 中文本换行"
echo ""
echo "=========================================="
