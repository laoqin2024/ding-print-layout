# 流程权限配置说明

## 概述

打印门户现在支持基于部门和用户的权限控制。您可以在 `print_layouts.json` 中为每个流程配置权限规则。

## 配置方式

在流程配置中添加 `permissions` 字段：

```json
{
  "PROC-XXXXX": {
    "name": "流程名称",
    "permissions": {
      "allowed_depts": ["部门A", "部门B"],
      "allowed_users": ["userid1", "userid2"]
    },
    "base_pdf": "...",
    "items": [...]
  }
}
```

## 权限规则

### 1. 无权限配置（默认）
如果流程没有配置 `permissions` 字段，则所有用户都可以看到该流程的审批单。

```json
{
  "PROC-XXXXX": {
    "name": "公开流程",
    "base_pdf": "template.pdf",
    "items": []
  }
}
```

### 2. 按部门限制
只有指定部门的用户才能看到该流程的审批单。

```json
{
  "PROC-XXXXX": {
    "name": "采购部专用流程",
    "permissions": {
      "allowed_depts": ["采购部", "物资管理部"]
    },
    "base_pdf": "template.pdf",
    "items": []
  }
}
```

### 3. 按用户限制
只有指定的用户才能看到该流程的审批单。

```json
{
  "PROC-XXXXX": {
    "name": "管理层专用流程",
    "permissions": {
      "allowed_users": ["022621450536936524", "0524373739-2137068346"]
    },
    "base_pdf": "template.pdf",
    "items": []
  }
}
```

### 4. 部门和用户组合
同时配置部门和用户限制，用户必须同时满足两个条件。

```json
{
  "PROC-XXXXX": {
    "name": "严格限制流程",
    "permissions": {
      "allowed_depts": ["总经办"],
      "allowed_users": ["022621450536936524"]
    },
    "base_pdf": "template.pdf",
    "items": []
  }
}
```

## 完整示例

```json
{
  "PROC-941085FC-98E5-4D84-8144-B81A054C17CB": {
    "name": "设计图纸变更通知单",
    "permissions": {
      "allowed_depts": ["品保部", "采购部", "计划部", "物资管理部", "欣兴汇事业部"]
    },
    "base_pdf": "主机厂图号更改通知单-无部门版本.pdf",
    "use_template": false,
    "orientation": "l",
    "items": [...]
  },
  "PROC-3AD62964-6C87-488F-9C66-0459940568CD": {
    "name": "主机客户订单打印",
    "permissions": {
      "allowed_depts": ["销售部", "计划部"]
    },
    "base_pdf": "",
    "use_template": false,
    "orientation": "p",
    "items": [...]
  },
  "PROC-06F848F3-2ADF-4209-B727-052DE489CFB5": {
    "name": "后勤物资申购单",
    "permissions": {
      "allowed_depts": ["行政部", "总经办"]
    },
    "base_pdf": "",
    "use_template": false,
    "orientation": "p",
    "items": [...]
  },
  "PROC-BD590F4C-385F-460A-B63E-45549E5238E7": {
    "name": "系统级外网账号开通",
    "permissions": {
      "allowed_depts": ["IT部", "总经办"],
      "allowed_users": ["022621450536936524"]
    },
    "base_pdf": "",
    "use_template": false,
    "orientation": "p",
    "items": [...]
  }
}
```

## 如何获取部门名称和用户ID

### 部门名称
1. 访问 `/admin/users` 人员管理页面
2. 查看用户列表中的"部门"列
3. 使用完整的部门名称（如"总经办"、"采购部"）

### 用户ID
1. 访问 `/admin/users` 人员管理页面
2. 查看用户列表中的"UserID"列
3. 复制完整的用户ID（如"022621450536936524"）

## 权限生效说明

1. **立即生效**：权限配置保存后立即生效，无需重启服务
2. **仅影响门户列表**：权限只控制打印门户中的流程列表显示，不影响直接访问打印页面
3. **基于用户信息**：权限检查基于 `data/users.json` 中的用户信息
4. **空配置开放**：如果 `allowed_depts` 或 `allowed_users` 为空数组，则该条件不生效

## 注意事项

1. 部门名称必须与 `users.json` 中的 `dept_name` 字段完全匹配（区分大小写）
2. 用户ID必须与 `users.json` 中的 `userid` 字段完全匹配
3. 如果用户信息在 `users.json` 中不存在，该用户将无法通过权限检查
4. 建议定期同步用户信息，确保权限配置准确
