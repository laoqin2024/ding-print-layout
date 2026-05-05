================================================================================
📋 Git 同步操作指南
================================================================================

由于 Git 操作需要较长时间，建议在终端中手动执行。

================================================================================
🚀 方式 1: 使用交互式脚本（推荐）
================================================================================

打开终端，执行以下命令:

```bash
cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
./sync_to_git_interactive.sh
```

脚本会逐步引导你完成同步过程。

================================================================================
🚀 方式 2: 手动执行命令
================================================================================

### 步骤 1: 进入项目目录

```bash
cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
```

### 步骤 2: 初始化 Git 仓库

```bash
git init
git config user.name "laoqin2024"
git config user.email "laoqin2024@users.noreply.github.com"
```

### 步骤 3: 添加文件

```bash
git add .
```

### 步骤 4: 查看将要提交的文件

```bash
git status
```

确认没有敏感文件（.env、process_configs.json 等）

### 步骤 5: 提交到本地仓库

```bash
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
```

### 步骤 6: 重命名主分支

```bash
git branch -M main
```

### 步骤 7: 添加远程仓库

```bash
git remote add github git@github.com:laoqin2024/ding-print-layout.git
git remote add gitee git@gitee.com:laoqin1/ding-print-layout.git
```

### 步骤 8: 推送到远程仓库

⚠️ **注意**: 推送前需要配置 SSH 密钥

- GitHub: https://github.com/settings/keys
- Gitee: https://gitee.com/profile/sshkeys

配置完成后执行:

```bash
# 推送到 GitHub
git push -u github main

# 推送到 Gitee
git push -u gitee main
```

================================================================================
🔑 SSH 密钥配置（如果还没配置）
================================================================================

### 1. 生成 SSH 密钥

```bash
ssh-keygen -t ed25519 -C "laoqin2024@users.noreply.github.com"
```

按回车使用默认路径，设置密码（可选）

### 2. 查看公钥

```bash
cat ~/.ssh/id_ed25519.pub
```

### 3. 添加到 GitHub

1. 访问 https://github.com/settings/keys
2. 点击 "New SSH key"
3. 粘贴公钥内容
4. 点击 "Add SSH key"

### 4. 添加到 Gitee

1. 访问 https://gitee.com/profile/sshkeys
2. 点击 "添加公钥"
3. 粘贴公钥内容
4. 点击 "确定"

### 5. 测试连接

```bash
# 测试 GitHub
ssh -T git@github.com

# 测试 Gitee
ssh -T git@gitee.com
```

================================================================================
⚠️ 如果仓库不存在
================================================================================

### 在 GitHub 上创建仓库

1. 访问 https://github.com/new
2. 仓库名: `ding-print-layout`
3. 描述: `钉钉打印排版系统`
4. 选择 Public 或 Private
5. **不要**勾选 "Initialize this repository with a README"
6. 点击 "Create repository"

### 在 Gitee 上创建仓库

1. 访问 https://gitee.com/projects/new
2. 仓库名: `ding-print-layout`
3. 描述: `钉钉打印排版系统`
4. 选择 公开 或 私有
5. **不要**勾选 "使用 Readme 文件初始化这个仓库"
6. 点击 "创建"

================================================================================
✅ 完成后
================================================================================

访问以下链接查看你的仓库:

- GitHub: https://github.com/laoqin2024/ding-print-layout
- Gitee: https://gitee.com/laoqin1/ding-print-layout

================================================================================
🔍 常见问题
================================================================================

### Q: 推送时提示 "Permission denied"

A: 需要配置 SSH 密钥，参见上面的 "SSH 密钥配置" 部分

### Q: 推送时提示 "Repository not found"

A: 需要先在 GitHub/Gitee 上创建仓库，参见上面的 "如果仓库不存在" 部分

### Q: 推送时提示 "Updates were rejected"

A: 远程仓库有内容，使用强制推送:
```bash
git push -u github main --force
git push -u gitee main --force
```

### Q: 如何更新已推送的代码？

A: 修改代码后执行:
```bash
git add .
git commit -m "更新说明"
git push
```

================================================================================
