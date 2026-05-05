# 流程权限配置示例

## 当前流程列表

根据 `print_layouts.json`，系统中有以下流程：

1. **设计图纸变更通知单** (PROC-941085FC-98E5-4D84-8144-B81A054C17CB)
2. **主机客户订单打印** (PROC-3AD62964-6C87-488F-9C66-0459940568CD)
3. **后勤物资申购单** (PROC-06F848F3-2ADF-4209-B727-052DE489CFB5)
4. **系统级外网账号开通** (PROC-BD590F4C-385F-460A-B63E-45549E5238E7)

## 推荐权限配置

### 方案一：按业务部门划分

```json
{
  "PROC-941085FC-98E5-4D84-8144-B81A054C17CB": {
    "name": "设计图纸变更通知单",
    "permissions": {
      "allowed_depts": [
        "技术中心一部",
        "技术中心二部",
        "技术一部",
        "技术二部",
        "技术工艺部",
        "品保",
        "质量部",
        "总经办"
      ]
    }
  },
  "PROC-3AD62964-6C87-488F-9C66-0459940568CD": {
    "name": "主机客户订单打印",
    "permissions": {
      "allowed_depts": [
        "国内主机部",
        "主机一部",
        "主机二部",
        "主机三部",
        "主机内勤",
        "计划部",
        "计划运营中心",
        "总经办"
      ]
    }
  },
  "PROC-06F848F3-2ADF-4209-B727-052DE489CFB5": {
    "name": "后勤物资申购单",
    "permissions": {
      "allowed_depts": [
        "后勤部",
        "基建/食堂",
        "综合办",
        "秘书办",
        "总经办"
      ]
    }
  },
  "PROC-BD590F4C-385F-460A-B63E-45549E5238E7": {
    "name": "系统级外网账号开通",
    "permissions": {
      "allowed_depts": [
        "信息化管理部",
        "总经办"
      ]
    }
  }
}
```

### 方案二：更宽松的配置（推荐用于初期）

```json
{
  "PROC-941085FC-98E5-4D84-8144-B81A054C17CB": {
    "name": "设计图纸变更通知单",
    "permissions": {
      "allowed_depts": [
        "技术中心一部",
        "技术中心二部",
        "技术一部",
        "技术二部",
        "技术工艺部",
        "品保",
        "质量部",
        "叶片泵主机品保",
        "方向机品保部",
        "空压机品保部",
        "包装部品保",
        "总经办"
      ]
    }
  },
  "PROC-3AD62964-6C87-488F-9C66-0459940568CD": {
    "name": "主机客户订单打印",
    "permissions": {
      "allowed_depts": [
        "国内主机部",
        "国内主机",
        "主机一部",
        "主机二部",
        "主机三部",
        "主机内勤",
        "叶片泵主机事业部",
        "计划部",
        "计划运营中心",
        "生产部",
        "总经办"
      ]
    }
  },
  "PROC-06F848F3-2ADF-4209-B727-052DE489CFB5": {
    "name": "后勤物资申购单",
    "permissions": {
      "allowed_depts": [
        "后勤部",
        "基建/食堂",
        "综合办",
        "秘书办",
        "人力资源部",
        "财务部",
        "总经办"
      ]
    }
  },
  "PROC-BD590F4C-385F-460A-B63E-45549E5238E7": {
    "name": "系统级外网账号开通",
    "permissions": {
      "allowed_depts": [
        "信息化管理部",
        "MES开发组",
        "SRM开发",
        "开发人员",
        "接口开发",
        "总经办"
      ]
    }
  }
}
```

### 方案三：特定用户 + 部门组合

```json
{
  "PROC-BD590F4C-385F-460A-B63E-45549E5238E7": {
    "name": "系统级外网账号开通",
    "permissions": {
      "allowed_depts": [
        "信息化管理部",
        "总经办"
      ],
      "allowed_users": [
        "022621450536936524",
        "0524373739-2137068346",
        "2206651766-461010822"
      ]
    }
  }
}
```

## 如何应用配置

### 步骤 1：备份当前配置

```bash
cd /root/dingtalk-h5-app/data
cp print_layouts.json print_layouts.json.backup
```

### 步骤 2：编辑配置文件

打开 `data/print_layouts.json`，为需要限制的流程添加 `permissions` 字段。

**示例：为"系统级外网账号开通"添加权限**

找到对应的流程配置：

```json
{
  "PROC-BD590F4C-385F-460A-B63E-45549E5238E7": {
    "name": "系统级外网账号开通",
    "base_pdf": "",
    "use_template": false,
    "orientation": "p",
    "cover_source_mode": "base",
    "cover_mode": "strict",
    "cover_offset_x": 0.0,
    "cover_offset_y": 0.0,
    "items": [...]
  }
}
```

添加 `permissions` 字段：

```json
{
  "PROC-BD590F4C-385F-460A-B63E-45549E5238E7": {
    "name": "系统级外网账号开通",
    "permissions": {
      "allowed_depts": ["信息化管理部", "总经办"]
    },
    "base_pdf": "",
    "use_template": false,
    "orientation": "p",
    "cover_source_mode": "base",
    "cover_mode": "strict",
    "cover_offset_x": 0.0,
    "cover_offset_y": 0.0,
    "items": [...]
  }
}
```

### 步骤 3：验证配置

```bash
cd /root/dingtalk-h5-app
python3 verify_permissions.py
```

检查输出，确保没有错误提示。

### 步骤 4：测试

1. 使用不同部门的用户账号登录钉钉
2. 访问打印门户
3. 验证权限是否按预期工作

## 常见问题

### Q1: 如何查看所有可用的部门名称？

运行验证脚本：
```bash
python3 verify_permissions.py
```

脚本会列出所有有效的部门名称。

### Q2: 配置后没有生效怎么办？

1. 检查 JSON 格式是否正确（使用 JSON 验证工具）
2. 确认部门名称与 `users.json` 中完全一致
3. 刷新浏览器页面（清除缓存）
4. 检查用户是否在 `users.json` 中

### Q3: 如何临时开放所有流程？

删除或注释掉 `permissions` 字段即可：

```json
{
  "PROC-XXXXX": {
    "name": "流程名称",
    // "permissions": {
    //   "allowed_depts": ["部门A"]
    // },
    "base_pdf": "..."
  }
}
```

### Q4: 总经办需要看到所有流程怎么办？

在每个流程的 `allowed_depts` 中都添加"总经办"：

```json
{
  "permissions": {
    "allowed_depts": ["其他部门", "总经办"]
  }
}
```

## 部门名称速查表

根据当前系统，以下是一些常用部门：

| 业务领域 | 部门名称 |
|---------|---------|
| 管理层 | 总经办、秘书办、综合办 |
| 技术研发 | 技术中心一部、技术中心二部、技术一部、技术二部、技术工艺部 |
| 质量品保 | 品保、质量部、叶片泵主机品保、方向机品保部、空压机品保部 |
| 销售业务 | 国内主机部、国内零售部、主机一部、主机二部、主机三部 |
| 生产制造 | 生产部、一车间、二车间、三车间、总装车间、机加工 |
| 计划物资 | 计划部、计划运营中心、物资管理部、采购一部、采购二部 |
| 后勤支持 | 后勤部、基建/食堂、人力资源部、财务部 |
| 信息化 | 信息化管理部、MES开发组、SRM开发、开发人员 |

## 下一步

1. 根据实际业务需求选择合适的配置方案
2. 逐步为流程添加权限配置
3. 定期审查和更新权限配置
4. 收集用户反馈，优化权限策略
