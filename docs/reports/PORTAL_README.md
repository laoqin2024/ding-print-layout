# 打印门户优化 - 快速参考

## 🎉 新功能

### 1️⃣ 流程模板筛选
在打印门户工具栏中，现在可以按流程模板快速筛选审批单。

### 2️⃣ 权限控制
支持基于部门和用户的流程访问权限控制，保护敏感流程。

### 3️⃣ 用户信息显示
页面顶部显示当前用户姓名和部门，方便确认身份。

---

## 🚀 快速开始

### 查看当前配置
```bash
cd /root/dingtalk-h5-app
python3 verify_permissions.py
```

### 为流程添加权限
编辑 `data/print_layouts.json`，添加 `permissions` 字段：

```json
{
  "PROC-XXXXX": {
    "name": "流程名称",
    "permissions": {
      "allowed_depts": ["部门A", "部门B"],
      "allowed_users": ["userid1", "userid2"]
    },
    "base_pdf": "template.pdf",
    "items": [...]
  }
}
```

### 验证配置
```bash
python3 verify_permissions.py
```

---

## 📚 详细文档

| 文档 | 说明 |
|------|------|
| [PORTAL_UPDATE_SUMMARY.md](PORTAL_UPDATE_SUMMARY.md) | 完整的更新总结 |
| [PORTAL_IMPROVEMENTS.md](PORTAL_IMPROVEMENTS.md) | 功能改进详细说明 |
| [data/PERMISSIONS_CONFIG_EXAMPLE.md](data/PERMISSIONS_CONFIG_EXAMPLE.md) | 权限配置语法 |
| [data/PERMISSION_SETUP_GUIDE.md](data/PERMISSION_SETUP_GUIDE.md) | 权限配置实战指南 |

---

## 💡 配置示例

### 示例 1：按部门限制
```json
{
  "PROC-XXXXX": {
    "name": "设计图纸变更通知单",
    "permissions": {
      "allowed_depts": ["技术中心一部", "品保", "总经办"]
    }
  }
}
```

### 示例 2：按用户限制
```json
{
  "PROC-XXXXX": {
    "name": "系统级外网账号开通",
    "permissions": {
      "allowed_users": ["022621450536936524", "0524373739-2137068346"]
    }
  }
}
```

### 示例 3：部门+用户组合
```json
{
  "PROC-XXXXX": {
    "name": "管理层专用流程",
    "permissions": {
      "allowed_depts": ["总经办"],
      "allowed_users": ["022621450536936524"]
    }
  }
}
```

---

## ✅ 测试清单

- [x] 权限检查逻辑测试通过
- [x] 配置验证工具测试通过
- [x] 前端构建成功
- [x] 文档完整

---

## 📞 需要帮助？

1. 运行 `python3 verify_permissions.py` 检查配置
2. 查看详细文档（见上方表格）
3. 联系系统管理员

---

**更新时间**: 2026-05-02  
**状态**: ✅ 就绪
