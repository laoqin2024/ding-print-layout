#!/bin/bash

# ================================================================================
# 钉钉打印排版系统 - Git 同步脚本（简化版）
# ================================================================================

set -e

echo "================================================================================"
echo "🚀 钉钉打印排版系统 - Git 同步到 GitHub 和 Gitee"
echo "================================================================================"
echo ""

# 进入项目目录
cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"

# 1. 初始化 Git 仓库
echo "步骤 1/8: 初始化 Git 仓库..."
if [ ! -d ".git" ]; then
    git init
    echo "✅ Git 仓库初始化完成"
else
    echo "⚠️  Git 仓库已存在"
fi

# 2. 配置 Git 用户
echo ""
echo "步骤 2/8: 配置 Git 用户..."
git config user.name "laoqin2024"
git config user.email "laoqin2024@users.noreply.github.com"
echo "✅ Git 用户配置完成"

# 3. 添加文件
echo ""
echo "步骤 3/8: 添加文件到 Git..."
git add .
echo "✅ 文件添加完成"

# 4. 查看将要提交的文件
echo ""
echo "步骤 4/8: 查看将要提交的文件..."
git status --short | head -20
echo ""
read -p "确认要提交这些文件吗？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 取消提交"
    exit 1
fi

# 5. 提交
echo ""
echo "步骤 5/8: 提交到本地仓库..."
git commit -m "Initial commit: 钉钉打印排版系统 v1.0.0

功能特性:
- 可视化排版设计器
- 多种控件类型支持
- 文本对齐功能（9种对齐方式）
- 附件底图功能
- 批量编辑功能
- 模板管理功能

技术栈:
- Flask + Python
- Vanilla JavaScript + Tailwind CSS
- ReportLab + DingTalk API

清理内容:
- 移除管理后台的新增配置功能
- 旧路由重定向到设计器"

echo "✅ 提交完成"

# 6. 重命名主分支
echo ""
echo "步骤 6/8: 重命名主分支为 main..."
git branch -M main
echo "✅ 主分支重命名完成"

# 7. 添加远程仓库
echo ""
echo "步骤 7/8: 添加远程仓库..."
git remote add github git@github.com:laoqin2024/ding-print-layout.git 2>/dev/null || echo "GitHub 远程仓库已存在"
git remote add gitee git@gitee.com:laoqin1/ding-print-layout.git 2>/dev/null || echo "Gitee 远程仓库已存在"
echo "✅ 远程仓库配置完成"

# 8. 推送到远程仓库
echo ""
echo "步骤 8/8: 推送到远程仓库..."
echo ""
echo "⚠️  注意: 推送需要配置 SSH 密钥"
echo "   GitHub: https://github.com/settings/keys"
echo "   Gitee: https://gitee.com/profile/sshkeys"
echo ""
read -p "是否已配置 SSH 密钥？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "请先配置 SSH 密钥，然后手动执行:"
    echo "  git push -u github main"
    echo "  git push -u gitee main"
    exit 0
fi

echo ""
echo "推送到 GitHub..."
git push -u github main

echo ""
echo "推送到 Gitee..."
git push -u gitee main

echo ""
echo "================================================================================"
echo "✅ 项目同步完成！"
echo "================================================================================"
echo ""
echo "GitHub 仓库: https://github.com/laoqin2024/ding-print-layout"
echo "Gitee 仓库: https://gitee.com/laoqin1/ding-print-layout"
echo ""
echo "================================================================================"
