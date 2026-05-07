#!/bin/bash

# ==========================================
# DingTalk Print Layout - 生产环境自动部署脚本
# ==========================================

# 确保脚本遇到错误立即退出
set -e

echo "🚀 开始自动部署流程..."

# 获取脚本所在目录的上一级目录（即项目根目录）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
echo "📂 当前工作目录: $PROJECT_ROOT"

# 1. 拉取最新代码
echo "⬇️ 正在从 Git 拉取最新代码..."
git fetch --all
# 可选：如果希望强制覆盖本地未经提交的修改，取消注释下一行
# git reset --hard origin/main
git pull origin main

# 2. 检查并创建虚拟环境
echo "🐍 检查 Python 虚拟环境..."
if [ ! -d "dingvenv" ]; then
    echo "⚠️ 未找到 dingvenv，正在创建..."
    python3 -m venv dingvenv
fi

# 3. 安装/更新依赖
echo "📦 正在安装/更新 Python 依赖..."
source dingvenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. 初始化缺失的配置文件（初次部署时起作用）
echo "⚙️ 检查配置和数据环境..."
mkdir -p data static/outputs templates/pdf_templates

if [ ! -f "data/print_layouts.json" ]; then
    echo "创建基础 data/print_layouts.json..."
    cp data/print_layouts.example.json data/print_layouts.json
fi

if [ ! -f "data/designer_stamp_assets.json" ]; then
    echo "创建基础 data/designer_stamp_assets.json..."
    cp data/designer_stamp_assets.example.json data/designer_stamp_assets.json
fi

# 5. 重启系统服务
echo "🔄 正在重启系统服务..."
# 检查系统是否配置了对应的服务
if systemctl list-unit-files | grep -q "dingtalk-print.service"; then
    sudo systemctl restart dingtalk-print
    echo "✅ 服务重启成功！"
    # 打印前几行状态确认运行正常
    sudo systemctl status dingtalk-print --no-pager | head -n 10
else
    echo "⚠️ 未检测到 dingtalk-print.service Systemd 服务。"
    echo "💡 如果您是初次部署，请参考 docs/DEPLOYMENT.md 配置 Systemd 守护进程。"
    echo "👉 临时手动启动命令: source dingvenv/bin/activate && gunicorn -w 4 -b 127.0.0.1:8000 run:app"
fi

echo "🎉 部署流程执行完毕！"
