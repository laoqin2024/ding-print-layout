#!/usr/bin/env python3
"""
检查和修复状态章 PNG 透明背景
"""

import sys
from pathlib import Path

# 添加项目路径（使用脚本所在目录）
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

import fitz

print("=" * 60)
print("检查状态章 PNG 文件")
print("=" * 60)
print()

stamps_dir = SCRIPT_DIR / "static/stamps"

# 查找所有 PNG 文件
png_files = list(stamps_dir.rglob("*.png"))

print(f"找到 {len(png_files)} 个 PNG 文件:")
print()

for png_file in png_files:
    print(f"文件: {png_file.relative_to(stamps_dir.parent)}")
    
    # 使用 PyMuPDF 检查
    try:
        # 创建临时 PDF 来检查图片
        doc = fitz.open()
        page = doc.new_page(width=200, height=200)
        
        # 插入图片
        rect = fitz.Rect(0, 0, 200, 200)
        page.insert_image(rect, filename=str(png_file))
        
        # 获取图片信息
        img_list = page.get_images()
        if img_list:
            xref = img_list[0][0]
            img_dict = doc.extract_image(xref)
            
            print(f"  格式: {img_dict['ext']}")
            print(f"  尺寸: {img_dict['width']}x{img_dict['height']}")
            print(f"  颜色空间: {img_dict.get('colorspace', 'N/A')}")
            
            # 检查是否有 alpha 通道
            # PNG 如果有透明通道，通常是 DeviceRGB + SMask
            if 'smask' in str(img_dict).lower():
                print(f"  ✅ 可能有透明通道")
            else:
                print(f"  ⚠️  可能没有透明通道")
        
        doc.close()
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
    
    print()

print("=" * 60)
print("建议")
print("=" * 60)
print()
print("如果 PNG 文件没有透明背景，需要：")
print("1. 使用 Photoshop/GIMP 等工具打开 PNG")
print("2. 删除白色背景，使其透明")
print("3. 保存为 PNG 格式（保留透明通道）")
print("4. 替换原文件")
print()
print("或者使用在线工具：")
print("  - https://www.remove.bg/")
print("  - https://onlinepngtools.com/create-transparent-png")
