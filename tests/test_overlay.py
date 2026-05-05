#!/usr/bin/env python3
"""
测试 PyMuPDF overlay 参数和 PNG 透明度
"""

import sys
import os
from pathlib import Path

# 添加项目路径（使用脚本所在目录）
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

import fitz

print("=" * 60)
print("PyMuPDF Overlay 测试")
print("=" * 60)
print()

# 1. 检查版本
print(f"1. PyMuPDF 版本: {fitz.version}")
print()

# 2. 创建测试 PDF
print("2. 创建测试 PDF...")
doc = fitz.open()
page = doc.new_page(width=595, height=842)

# 绘制底图（红色矩形）
rect = fitz.Rect(100, 100, 300, 300)
page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0, 0))
page.insert_text((110, 120), "底图内容", fontsize=20)

# 3. 测试插入 PNG（不使用 overlay）
print("3. 测试插入 PNG（overlay=False）...")
stamp_path = SCRIPT_DIR / "static/stamps/client/agree.png"
if stamp_path.exists():
    rect2 = fitz.Rect(150, 150, 250, 250)
    try:
        page.insert_image(rect2, filename=str(stamp_path), keep_proportion=True, rotate=0, overlay=False)
        print("   ✅ overlay=False 插入成功")
    except Exception as e:
        print(f"   ❌ 插入失败: {e}")
else:
    print(f"   ❌ 文件不存在: {stamp_path}")

# 保存测试1
output1 = Path("/tmp/test_overlay_false.pdf")
doc.save(str(output1))
print(f"   保存到: {output1}")
doc.close()

# 4. 测试插入 PNG（使用 overlay）
print()
print("4. 测试插入 PNG（overlay=True）...")
doc = fitz.open()
page = doc.new_page(width=595, height=842)

# 绘制底图（红色矩形）
rect = fitz.Rect(100, 100, 300, 300)
page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0, 0))
page.insert_text((110, 120), "底图内容", fontsize=20)

if stamp_path.exists():
    rect2 = fitz.Rect(150, 150, 250, 250)
    try:
        page.insert_image(rect2, filename=str(stamp_path), keep_proportion=True, rotate=0, overlay=True)
        print("   ✅ overlay=True 插入成功")
    except Exception as e:
        print(f"   ❌ 插入失败: {e}")

# 保存测试2
output2 = Path("/tmp/test_overlay_true.pdf")
doc.save(str(output2))
print(f"   保存到: {output2}")
doc.close()

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
print()
print("请对比两个 PDF 文件：")
print(f"  - {output1} (overlay=False)")
print(f"  - {output2} (overlay=True)")
print()
print("如果 overlay=True 有效，应该能看到底图的红色内容")
print("如果 PNG 有透明背景，应该能看到红色背景")
