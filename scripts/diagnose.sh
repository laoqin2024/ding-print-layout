#!/bin/bash

echo "=== 设计器问题诊断脚本 ==="
echo ""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "1. 检查文件修改时间："
echo "   designer_edit.js: $(stat -f '%Sm' "$SCRIPT_DIR/static/js/designer_edit.js")"
echo "   designer.py: $(stat -f '%Sm' "$SCRIPT_DIR/app/routes/designer.py")"
echo ""

echo "2. 检查状态章 overlay 参数："
grep -n "stamp_path.*insert_image" "$SCRIPT_DIR/app/routes/designer.py" -A 1 | head -5
echo ""

echo "3. 检查签名 overlay 参数："
grep -n "sig_fill_mode.*auto_sequence" "$SCRIPT_DIR/app/routes/designer.py" -A 10 | grep "insert_image"
echo ""

echo "4. 检查部门控件换行代码："
grep -n "r === \"dept\"" "$SCRIPT_DIR/static/js/designer_edit.js" -A 5 | head -10
echo ""

echo "5. 检查 PNG 文件透明通道："
file "$SCRIPT_DIR/static/stamps/client/agree.png"
echo ""

echo "=== 诊断完成 ==="
echo ""
echo "如果以上检查都正确，请执行以下操作："
echo "1. 重启 Flask 服务器"
echo "2. 在浏览器中强制刷新（Ctrl+Shift+R）"
echo "3. 选中部门控件，勾选'文本自动换行'"
echo "4. 点击'更新选中项'按钮"
echo "5. 点击'保存布局'按钮"
echo "6. 预览 PDF 查看效果"
