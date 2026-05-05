# 钉钉打印排版系统

一个基于 Flask 的钉钉审批流程打印排版系统，支持可视化设计器、权限管理和 PDF 生成。

## ✨ 功能特性

### 🎨 可视化排版设计器
- **拖拽式设计**: 直观的拖拽操作，快速创建打印模板
- **多种控件**: 支持文本、日期、图片、二维码、签名、印章等多种控件
- **实时预览**: 所见即所得的设计体验
- **模板管理**: 支持模板的保存、加载、复制和删除
- **空白模板**: 支持横向和纵向空白模板，从零开始设计

### 📄 控件类型
- **文本控件**: 支持字体、字号、颜色、粗细、斜体等样式
- **日期控件**: 自动格式化日期显示
- **标签控件**: 静态文本标签
- **图片控件**: 支持 URL 和上传
- **二维码**: 动态生成二维码
- **签名**: 集成钉钉签名
- **印章**: 支持状态印章
- **部门**: 显示部门信息
- **流程结果**: 显示审批结果

### 🎯 高级功能
- **文本对齐**: 支持 9 种对齐方式（左上、左中、左下、中上、中中、中下、右上、右中、右下）
- **附件底图**: 支持使用审批附件作为 PDF 底图
- **批量编辑**: 支持多个控件的批量属性修改
- **撤销/重做**: 完整的操作历史记录
- **网格对齐**: 辅助精确定位
- **缩放功能**: 支持画布缩放查看

### 🔐 权限管理系统
- **系统管理员**: 配置系统管理员，管理员可查看所有审批
- **部门主管**: 自动从钉钉同步，主管可查看本部门成员的审批
- **模板权限**: 配置模板的可见范围（所有人/指定部门）
- **查看权限**: 配置额外查看者（部门主管/指定用户）
- **权限统计**: 实时显示用户、部门、主管数量

### 🔧 系统功能
- **钉钉集成**: 与钉钉审批流程深度集成
- **PDF 生成**: 高质量 PDF 输出
- **用户管理**: 管理系统用户
- **签名绑定**: 绑定用户签名
- **版本管理**: 模板版本控制和回滚

## 📋 系统要求

- Python 3.8+
- Flask 2.0+
- 钉钉企业账号

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/laoqin2024/ding-print-layout.git
cd ding-print-layout
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写以下必需配置：

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

### 4. 创建必要的目录

```bash
mkdir -p static/outputs
mkdir -p templates/pdf_templates
mkdir -p data
```

### 5. 运行应用

```bash
python run.py
```

应用将在 `http://localhost:8000` 启动。

## 📖 使用指南

### 访问设计器

访问 `http://localhost:8000/designer` 进入可视化设计器。

### 创建模板

1. 点击"新增模板"按钮
2. 选择模板类型（横向/纵向）
3. 拖拽控件到画布
4. 配置控件属性
5. 保存模板

### 配置权限

1. 访问 `http://localhost:8000/admin/permissions`
2. 配置系统管理员
3. 设置模板可见范围
4. 查看部门主管列表

### 打印预览

1. 在钉钉中提交审批
2. 系统自动生成 PDF
3. 可在打印门户查看和下载

## 🏗️ 项目结构

```
dingtalk-h5-app/
├── app/
│   ├── __init__.py              # Flask 应用初始化
│   ├── config.py                # 配置管理
│   ├── routes/                  # 路由模块
│   │   ├── admin.py             # 管理后台路由
│   │   ├── designer.py          # 设计器路由
│   │   ├── permissions.py       # 权限管理路由
│   │   ├── portal.py            # 打印门户路由
│   │   ├── printing.py          # 打印路由
│   │   └── users.py             # 用户管理路由
│   └── services/                # 服务模块
│       ├── dingtalk_service.py  # 钉钉 API 服务
│       ├── pdf_service.py       # PDF 生成服务
│       └── permission_service.py # 权限控制服务
├── static/                      # 静态资源
│   ├── css/                     # 样式文件
│   ├── js/                      # JavaScript 文件
│   │   └── designer_edit.js     # 设计器核心逻辑
│   └── outputs/                 # PDF 输出目录
├── templates/                   # HTML 模板
│   ├── designer_edit.html       # 设计器页面
│   ├── designer_print.html      # 打印预览页面
│   ├── print.html               # 打印门户页面
│   ├── permissions/             # 权限管理页面
│   │   ├── index.html           # 权限管理主页
│   │   ├── admins.html          # 系统管理员配置
│   │   ├── managers.html        # 部门主管查看
│   │   └── templates.html       # 模板权限配置
│   └── pdf_templates/           # PDF 模板目录
├── data/                        # 数据文件
│   ├── print_layouts.json       # 打印布局配置
│   ├── business_permissions.json # 业务权限配置
│   ├── users.json               # 用户数据（不提交）
│   └── process_configs.json     # 流程配置（不提交）
├── scripts/                     # 脚本工具
│   └── upgrade_users_json.py    # 用户数据升级脚本
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git 忽略文件
├── requirements.txt             # Python 依赖
├── run.py                       # 应用入口
└── README.md                    # 项目文档
```

## 🔒 安全说明

### 敏感信息保护

以下文件包含敏感信息，**不会**提交到 Git 仓库：

- `.env` - 环境变量和密钥
- `data/process_configs.json` - 流程配置
- `data/users.json` - 用户数据
- `data/signature_bindings.json` - 签名绑定
- `templates/pdf_templates/*.pdf` - PDF 模板
- `static/outputs/*.pdf` - 生成的 PDF

### 首次部署

1. 复制 `.env.example` 为 `.env`
2. 填写钉钉凭证和密钥
3. 创建必要的数据文件
4. 运行用户数据升级脚本（如需权限功能）

## 🛠️ 开发指南

### 添加新控件类型

1. 在 `designer_edit.js` 中添加控件配置
2. 在 `pdf_service.py` 中添加渲染逻辑
3. 更新控件参数配置

### 修改样式

- 项目使用 Tailwind CSS
- 自定义样式在 `static/css/` 目录

### 调试

- 开启 Flask 调试模式：在 `.env` 中设置 `FLASK_DEBUG=1`
- 查看浏览器控制台日志
- 查看服务器终端日志

## 📝 更新日志

### v1.1.0 (2026-05-05)

**新增功能**:
- ✅ 权限管理系统
  - 系统管理员配置
  - 部门主管自动同步
  - 模板权限配置
  - 权限统计展示
- ✅ 用户数据升级脚本
- ✅ PC 端优化的管理界面

**优化改进**:
- ✅ 修复背景闪烁问题
- ✅ 修复列表滚动抖动
- ✅ 优化部门选择器
- ✅ 改进权限判断逻辑

### v1.0.0 (2026-05-04)

- ✅ 可视化排版设计器
- ✅ 多种控件类型支持
- ✅ 文本对齐功能（9 种对齐方式）
- ✅ 附件底图功能
- ✅ 批量编辑功能
- ✅ 模板管理功能
- ✅ 空白模板支持

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

laoqin2024

## 🔗 相关链接

- [GitHub 仓库](https://github.com/laoqin2024/ding-print-layout)
- [Gitee 仓库](https://gitee.com/laoqin1/ding-print-layout)
- [钉钉开放平台](https://open.dingtalk.com/)

## ❓ 常见问题

### Q: 如何获取钉钉凭证？

A: 登录钉钉开放平台，创建应用后可获取 APP_KEY 和 APP_SECRET。

### Q: 如何配置权限管理？

A: 
1. 运行用户数据升级脚本：`python scripts/upgrade_users_json.py`
2. 访问权限管理页面：`http://localhost:8000/admin/permissions`
3. 配置系统管理员和模板权限

### Q: PDF 生成失败怎么办？

A: 检查以下几点：
1. 确认 PDF 模板文件存在
2. 检查字段映射是否正确
3. 查看服务器日志获取详细错误信息

### Q: 如何备份数据？

A: 备份以下文件和目录：
- `data/` 目录下的所有 JSON 文件
- `templates/pdf_templates/` 目录下的 PDF 模板
- `.env` 配置文件

### Q: 支持哪些浏览器？

A: 推荐使用现代浏览器：
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 📞 支持

如有问题，请提交 Issue 或联系作者。
