================================================================================
🚀 钉钉打印排版系统 - 快速启动指南
================================================================================

## 📋 目录

1. [系统要求](#系统要求)
2. [快速开始](#快速开始)
3. [配置说明](#配置说明)
4. [功能使用](#功能使用)
5. [常见问题](#常见问题)
6. [Git 同步](#git-同步)

---

## 系统要求

- Python 3.8+
- pip (Python 包管理器)
- 钉钉企业账号
- 钉钉应用（需要 APP_KEY 和 APP_SECRET）

---

## 快速开始

### 1. 安装依赖

```bash
cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
nano .env
```

填写以下必需配置：

```env
# 钉钉凭证（必需）
DINGTALK_APP_KEY=your_app_key
DINGTALK_APP_SECRET=your_app_secret
DINGTALK_CORP_ID=your_corp_id

# Flask 密钥（必需）
FLASK_SECRET_KEY=your_random_secret_key

# 服务器端口（可选，默认 8000）
PORT=8000

# 公网访问地址（用于钉钉回调）
PUBLIC_BASE_URL=http://your-domain.com:8000
```

### 3. 启动应用

```bash
python run.py
```

应用将在 `http://localhost:8000` 启动。

### 4. 访问设计器

打开浏览器访问：`http://localhost:8000/designer`

---

## 配置说明

### 获取钉钉凭证

1. 登录钉钉开放平台：https://open.dingtalk.com/
2. 创建应用或选择现有应用
3. 获取 `APP_KEY` 和 `APP_SECRET`
4. 获取企业 `CORP_ID`

### 生成 Flask 密钥

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 配置公网访问

如果需要钉钉回调功能，需要配置公网访问地址：

1. 使用内网穿透工具（如 ngrok）
2. 或者部署到公网服务器
3. 在 `.env` 中设置 `PUBLIC_BASE_URL`

---

## 功能使用

### 1. 创建模板

1. 访问设计器：`http://localhost:8000/designer`
2. 点击"新增模板"
3. 选择模板类型（横向/纵向）
4. 输入模板名称和流程 code
5. 点击"创建"

### 2. 设计排版

1. 从左侧工具栏拖拽控件到画布
2. 选中控件，在右侧属性面板配置参数：
   - 位置和尺寸（X, Y, W, H）
   - 显示文本（label）
   - 字段绑定（field_id, field_name, field_type）
   - 字体样式（字体、字号、颜色、粗细）
   - **水平对齐**：左对齐/居中/右对齐
   - **垂直对齐**：顶部/居中/底部
   - 其他参数（行高、字间距等）
3. 点击"更新选中项"保存修改

### 3. 批量编辑

1. 按住 Shift 或 Ctrl 选择多个控件
2. 在属性面板中修改参数
3. 点击"更新选中项"
4. 所有选中的控件都会被更新

### 4. 保存模板

1. 点击"保存模板"按钮
2. 模板会保存到 `data/print_layouts.json`

### 5. 预览 PDF

1. 点击"预览 PDF"按钮
2. 系统会生成预览 PDF
3. 可以下载查看效果

---

## 常见问题

### Q1: 启动时提示 "ModuleNotFoundError"

**A**: 需要安装依赖

```bash
pip install -r requirements.txt
```

### Q2: 访问设计器显示 404

**A**: 检查服务器是否正常启动，查看终端日志

### Q3: 参数面板不显示

**A**: 
1. 强制刷新浏览器（Ctrl+Shift+R 或 Cmd+Shift+R）
2. 清除浏览器缓存
3. 检查浏览器控制台是否有 JavaScript 错误

### Q4: 垂直对齐不生效

**A**: 
1. 确保控件高度足够大（H > 字号）
2. 保存模板后重新预览 PDF
3. 检查后端是否支持 vertical_align 参数

### Q5: PDF 生成失败

**A**: 
1. 检查 PDF 模板文件是否存在
2. 检查字段映射是否正确
3. 查看服务器日志获取详细错误信息

### Q6: 钉钉认证失败

**A**: 
1. 检查 `.env` 中的钉钉凭证是否正确
2. 确认应用已发布并授权
3. 检查 CORP_ID 是否正确

---

## Git 同步

### 同步到 GitHub 和 Gitee

```bash
cd "/Volumes/MyDisk/App programs/dingtalk-h5-app"
./sync_to_git_interactive.sh
```

或者查看详细指南：

```bash
cat GIT_SYNC_GUIDE.md
```

### 更新代码

修改代码后：

```bash
git add .
git commit -m "更新说明"
git push
```

---

## 📁 项目结构

```
dingtalk-h5-app/
├── app/                      # 应用核心代码
│   ├── routes/               # 路由模块
│   │   ├── designer.py       # 设计器路由 ⭐
│   │   ├── portal.py         # 打印门户
│   │   ├── printing.py       # 打印功能
│   │   ├── admin.py          # 管理后台
│   │   └── users.py          # 用户管理
│   └── services/             # 服务模块
│       ├── pdf_service.py    # PDF 生成 ⭐
│       └── dingtalk_service.py # 钉钉 API
├── static/
│   └── js/
│       └── designer_edit.js  # 设计器核心逻辑 ⭐
├── templates/
│   └── designer_edit.html    # 设计器页面 ⭐
├── data/
│   └── print_layouts.json    # 打印布局配置 ⭐
├── .env                      # 环境变量（不提交）
├── .env.example              # 环境变量示例
├── requirements.txt          # Python 依赖
└── run.py                    # 应用入口
```

⭐ = 核心文件

---

## 🎯 核心功能

### 1. 可视化设计器
- 拖拽式操作
- 实时预览
- 所见即所得

### 2. 控件类型
- 文本框（text）
- 日期（date）
- 标签（label）
- 图片（image）
- 二维码（qrcode）
- 签名（signature）
- 印章（status_stamp）
- 部门（dept）
- 流程结果（flow_result）

### 3. 文本对齐
- **水平对齐**: 左/中/右
- **垂直对齐**: 上/中/下
- **组合**: 9 种对齐方式

### 4. 高级功能
- 批量编辑
- 撤销/重做
- 网格对齐
- 缩放功能
- 附件底图

---

## 🔗 相关链接

- **GitHub**: https://github.com/laoqin2024/ding-print-layout
- **Gitee**: https://gitee.com/laoqin1/ding-print-layout
- **钉钉开放平台**: https://open.dingtalk.com/

---

## 📞 支持

如有问题，请：
1. 查看本文档的"常见问题"部分
2. 查看 `README.md` 获取更多信息
3. 提交 Issue 到 GitHub/Gitee

---

## 📝 更新日志

### v1.0.0 (2026-05-05)

- ✅ 可视化排版设计器
- ✅ 多种控件类型支持
- ✅ 文本对齐功能（9 种对齐方式）
- ✅ 附件底图功能
- ✅ 批量编辑功能
- ✅ 模板管理功能
- ✅ 空白模板支持
- ✅ 清理管理后台的"新增配置"功能

---

## ⚡ 快速命令参考

```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python run.py

# 查看日志
tail -f logs/app.log

# Git 同步
./sync_to_git_interactive.sh

# 查看帮助
cat QUICK_START.md
```

---

**祝你使用愉快！** 🎉

================================================================================
