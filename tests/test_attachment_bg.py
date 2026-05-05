#!/usr/bin/env python3
"""
测试附件底图功能
"""

import sys
from pathlib import Path

# 添加项目路径（使用脚本所在目录）
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR))

print("=" * 80)
print("附件底图功能测试")
print("=" * 80)
print()

# 1. 检查代码修改
print("1. 检查代码修改...")
print("-" * 80)

designer_py = SCRIPT_DIR / "app/routes/designer.py"
content = designer_py.read_text()

checks = [
    ("attachment_background_config", "读取附件底图配置"),
    ("attachment_bg_enabled", "启用标志"),
    ("attachment_bg_field_id", "字段ID"),
    ("attachment_bg_index", "附件索引"),
    ("attachment_bg_page", "页码"),
    ("download_specific_attachment_pdf", "下载指定附件"),
]

for pattern, desc in checks:
    if pattern in content:
        print(f"✅ {desc}: {pattern}")
    else:
        print(f"❌ {desc}: {pattern} 未找到")

print()

# 2. 检查 DingTalkService
print("2. 检查 DingTalkService...")
print("-" * 80)

dingtalk_service = SCRIPT_DIR / "app/services/dingtalk_service.py"
service_content = dingtalk_service.read_text()

if "def download_specific_attachment_pdf" in service_content:
    print("✅ download_specific_attachment_pdf 方法已添加")
    
    # 检查参数
    if "field_id" in service_content and "attachment_index" in service_content:
        print("✅ 方法参数正确")
    else:
        print("❌ 方法参数不完整")
else:
    print("❌ download_specific_attachment_pdf 方法未找到")

print()

# 3. 检查配置示例
print("3. 检查配置示例...")
print("-" * 80)

import json

layouts_file = SCRIPT_DIR / "data/print_layouts.json"
if layouts_file.exists():
    with open(layouts_file, 'r', encoding='utf-8') as f:
        layouts = json.load(f)
    
    has_attachment_config = False
    for code, layout in layouts.items():
        if "attachment_background_config" in layout:
            config = layout["attachment_background_config"]
            if config.get("enabled"):
                has_attachment_config = True
                print(f"✅ 找到附件底图配置: {code}")
                print(f"   字段ID: {config.get('field_id')}")
                print(f"   附件索引: {config.get('attachment_index')}")
                print(f"   页码: {config.get('page_index')}")
                print(f"   应用模式: {config.get('apply_mode')}")
                break
    
    if not has_attachment_config:
        print("⚠️  没有找到启用的附件底图配置")
else:
    print("❌ 布局配置文件不存在")

print()

# 4. 使用说明
print("=" * 80)
print("使用说明")
print("=" * 80)
print()
print("1. 在设计器中配置附件底图：")
print("   - 勾选'启用'")
print("   - 选择附件字段（如 DDAttachment_1PKSP5YV9WRGG）")
print("   - 设置附件索引（第几个附件，从 0 开始）")
print("   - 设置 PDF 页码（第几页，从 0 开始）")
print("   - 选择应用模式：")
print("     * preview_and_print - 预览和打印都使用附件")
print("     * print_only - 仅打印时使用附件")
print()
print("2. 保存布局配置")
print()
print("3. 在钉钉中预览打印：")
print("   - 填写实例 ID")
print("   - 点击预览")
print("   - 应该能看到附件底图")
print()
print("=" * 80)
print("测试完成")
print("=" * 80)
