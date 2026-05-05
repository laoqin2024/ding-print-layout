#!/bin/bash

# ================================================================================
# 钉钉打印排版系统 - Git 同步脚本
# ================================================================================

set -e

PROJECT_DIR="/Volumes/MyDisk/App programs/dingtalk-h5-app"
cd "$PROJECT_DIR"

echo "================================================================================"
echo "🚀 开始准备项目同步到 GitHub 和 Gitee"
echo "================================================================================"

# 1. 检查敏感文件
echo ""
echo "📋 步骤 1/7: 检查敏感文件..."
if [ -f ".env" ]; then
    echo "✅ .env 文件存在（将被 .gitignore 忽略）"
else
    echo "⚠️  .env 文件不存在，请从 .env.example 复制并配置"
fi

# 2. 初始化 Git 仓库
echo ""
echo "📋 步骤 2/7: 初始化 Git 仓库..."
if [ -d ".git" ]; then
    echo "⚠️  Git 仓库已存在，跳过初始化"
else
    git init
    echo "✅ Git 仓库初始化完成"
fi

# 3. 配置 Git 用户
echo ""
echo "📋 步骤 3/7: 配置 Git 用户..."
git config user.name "laoqin2024"
git config user.email "laoqin2024@users.noreply.github.com"
echo "✅ Git 用户配置完成"

# 4. 添加文件
echo ""
echo "📋 步骤 4/7: 添加文件到 Git..."
git add .
echo "✅ 文件添加完成"

# 5. 提交
echo ""
echo "📋 步骤 5/7: 提交到本地仓库..."
git commit -m "Initial commit: 钉钉打印排版系统 v1.0.0

功能特性:
- 可视化排版设计器
- 多种控件类型支持（文本、日期、图片、二维码、签名、印章等）
- 文本对齐功能（支持9种对齐方式：左上、左中、左下、中上、中中、中下、右上、右中、右下）
- 附件底图功能
- 批量编辑功能
- 模板管理功能
- 空白模板支持
- 撤销/重做功能
- 网格对齐辅助
- 缩放功能

技术栈:
- 后端: Flask + Python
- 前端: Vanilla JavaScript + Tailwind CSS
- PDF 生成: ReportLab
- 钉钉集成: DingTalk Open API

安全特性:
- 敏感信息通过 .gitignore 保护
- 环境变量配置
- 用户权限管理"

echo "✅ 提交完成"

# 6. 添加远程仓库
echo ""
echo "📋 步骤 6/7: 添加远程仓库..."
git remote add github git@github.com:laoqin2024/ding-print-layout.git 2>/dev/null || echo "GitHub 远程仓库已存在"
git remote add gitee git@gitee.com:laoqin1/ding-print-layout.git 2>/dev/null || echo "Gitee 远程仓库已存在"
echo "✅ 远程仓库配置完成"

# 7. 推送到远程仓库
echo ""
echo "📋 步骤 7/7: 推送到远程仓库..."
git branch -M main

echo ""
echo "推送到 GitHub..."
git push -u github main --force

echo ""
echo "推送到 Gitee..."
git push -u gitee main --force

echo ""
echo "================================================================================"
echo "✅ 项目同步完成！"
echo "================================================================================"
echo ""
echo "GitHub 仓库: https://github.com/laoqin2024/ding-print-layout"
echo "Gitee 仓库: https://gitee.com/laoqin1/ding-print-layout"
echo ""
echo "================================================================================"
