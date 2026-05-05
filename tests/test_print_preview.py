#!/usr/bin/env python3
"""
测试钉钉打印预览附件底图功能
"""

import sys
from pathlib import Path
import json

# 添加项目路径（使用脚本所在目录）
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

print("=" * 80)
print("钉钉打印预览附件底图功能测试")
print("=" * 80)
print()

# 1. 检查 designer_preview_print 函数
print("1. 检查 designer_preview_print 函数...")
print("-" * 80)

designer_py = SCRIPT_DIR / "app/routes/designer.py"
content = designer_py.read_text()

# 查找 designer_preview_print 函数
if "def designer_preview_print" in content:
    print("✅ designer_preview_print 函数存在")
    
    # 检查是否包含 attachment_background_config
    lines = content.split('\n')
    in_function = False
    has_attachment_config = False
    
    for i, line in enumerate(lines):
        if 'def designer_preview_print' in line:
            in_function = True
        elif in_function and 'def ' in line and 'designer_preview_print' not in line:
            break
        elif in_function and 'attachment_background_config' in line:
            has_attachment_config = True
            print(f"✅ 包含 attachment_background_config（第 {i+1} 行）")
            break
    
    if not has_attachment_config:
        print("❌ 未包含 attachment_background_config")
else:
    print("❌ designer_preview_print 函数不存在")

print()

# 2. 检查 designer_preview 函数
print("2. 检查 designer_preview 函数...")
print("-" * 80)

if "def designer_preview" in content:
    print("✅ designer_preview 函数存在")
    
    # 检查是否读取 attachment_background_config
    if "attachment_bg_config = payload.get" in content:
        print("✅ 读取 attachment_background_config")
    else:
        print("❌ 未读取 attachment_background_config")
    
    # 检查是否使用 download_specific_attachment_pdf
    if "download_specific_attachment_pdf" in content:
        print("✅ 使用 download_specific_attachment_pdf")
    else:
        print("❌ 未使用 download_specific_attachment_pdf")
else:
    print("❌ designer_preview 函数不存在")

print()

# 3. 检查配置
print("3. 检查布局配置...")
print("-" * 80)

layouts_file = SCRIPT_DIR / "data/print_layouts.json"
if layouts_file.exists():
    with open(layouts_file, 'r', encoding='utf-8') as f:
        layouts = json.load(f)
    
    for code, layout in layouts.items():
        if "attachment_background_config" in layout:
            config = layout["attachment_background_config"]
            if config.get("enabled"):
                print(f"✅ 流程: {code}")
                print(f"   名称: {layout.get('name')}")
                print(f"   启用: {config.get('enabled')}")
                print(f"   字段ID: {config.get('field_id')}")
                print(f"   附件索引: {config.get('attachment_index')}")
                print(f"   页码: {config.get('page_index')}")
                print(f"   应用模式: {config.get('apply_mode')}")
                print()
                
                # 生成测试 URL
                print(f"   测试 URL:")
                print(f"   http://localhost:5000/designer/preview_print?process_code={code}&instance_id=YOUR_INSTANCE_ID")
                print()
else:
    print("❌ 布局配置文件不存在")

print()

# 4. 测试流程
print("=" * 80)
print("测试流程")
print("=" * 80)
print()
print("1. 确认配置正确")
print("   - 附件底图配置已启用")
print("   - 字段ID、附件索引、页码都已设置")
print("   - 应用模式为 'preview_and_print'")
print()
print("2. 在钉钉中测试")
print("   - 打开审批实例")
print("   - 点击'打印预览'")
print("   - 应该能看到附件底图")
print()
print("3. 如果还是看不到")
print("   - 检查服务器日志: tail -f /tmp/dingtalk-app.log")
print("   - 检查实例是否有附件")
print("   - 检查附件是否是 PDF 格式")
print("   - 检查附件索引是否正确")
print()
print("=" * 80)
print("测试完成")
print("=" * 80)
