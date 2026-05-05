#!/bin/bash

echo "=== 修复系统自检默认数据 ==="
echo ""

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. 恢复 process_configs.json
echo "1. 恢复 process_configs.json..."
if [ -f data/process_configs.history.json ]; then
    # 从历史中提取最新的配置
    python3 << 'EOF'
import json

# 读取历史
with open('data/process_configs.history.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

# 提取所有唯一的 process_code
configs = {}
for entry in history:
    code = entry.get('process_code')
    if code and 'previous' in entry:
        configs[code] = entry['previous']

# 保存
with open('data/process_configs.json', 'w', encoding='utf-8') as f:
    json.dump(configs, f, ensure_ascii=False, indent=2)

print(f"✅ 恢复了 {len(configs)} 个流程配置")
EOF
else
    echo "❌ 未找到历史备份文件"
fi

echo ""

# 2. 创建默认的 base_pdf 配置
echo "2. 创建默认 PDF 模板配置..."
python3 << 'EOF'
import json
import os

# 检查 PDF 模板目录
pdf_dir = 'templates/pdf_templates'
if os.path.exists(pdf_dir):
    pdfs = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    print(f"✅ 找到 {len(pdfs)} 个 PDF 模板")
    for pdf in pdfs[:5]:
        print(f"   - {pdf}")
else:
    print("❌ PDF 模板目录不存在")

# 读取当前配置
with open('data/process_configs.json', 'r', encoding='utf-8') as f:
    configs = json.load(f)

# 确保每个配置都有 base_pdf
updated = 0
for code, config in configs.items():
    if not config.get('base_pdf') and pdfs:
        # 尝试匹配名称
        name = config.get('name', '')
        matched = False
        for pdf in pdfs:
            if name in pdf or pdf.replace('.pdf', '') in name:
                config['base_pdf'] = pdf
                matched = True
                updated += 1
                break
        if not matched and pdfs:
            config['base_pdf'] = pdfs[0]
            updated += 1

if updated > 0:
    with open('data/process_configs.json', 'w', encoding='utf-8') as f:
        json.dump(configs, f, ensure_ascii=False, indent=2)
    print(f"✅ 更新了 {updated} 个配置的 base_pdf")
EOF

echo ""

# 3. 检查结果
echo "3. 检查修复结果..."
python3 << 'EOF'
import json

with open('data/process_configs.json', 'r', encoding='utf-8') as f:
    configs = json.load(f)

print(f"流程配置数量: {len(configs)}")
for code, config in list(configs.items())[:3]:
    print(f"  - {code}: {config.get('name', 'N/A')}")
    print(f"    base_pdf: {config.get('base_pdf', 'N/A')}")
EOF

echo ""
echo "=== 修复完成 ==="
echo ""
echo "请刷新浏览器并重新访问 /admin/health 检查"
