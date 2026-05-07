# 流程权限配置指南

## 当前流程列表

在 `print_layouts.json` 中，你可以找到所有配置好的打印流程，例如：

1. **示例表单 A** (PROC-EXAMPLE-FORM-A)
2. **示例表单 B** (PROC-EXAMPLE-FORM-B)

## 推荐权限配置策略

### 方案一：按业务部门划分

为不同业务领域的表单限制相应的可见部门。

```json
{
  "PROC-EXAMPLE-FORM-A": {
    "name": "示例表单 A",
    "permissions": {
      "allowed_depts": [
        "研发一部",
        "研发二部",
        "测试部",
        "管理层"
      ]
    }
  },
  "PROC-EXAMPLE-FORM-B": {
    "name": "示例表单 B",
    "permissions": {
      "allowed_depts": [
        "销售一部",
        "销售二部",
        "市场部",
        "管理层"
      ]
    }
  }
}
```

### 方案二：特定用户 + 部门组合

用于极高保密级别的流程。

```json
{
  "PROC-EXAMPLE-SECRET": {
    "name": "核心机密表单",
    "permissions": {
      "allowed_depts": [
        "管理层"
      ],
      "allowed_users": [
        "admin01",
        "admin02"
      ]
    }
  }
}
```

## 如何应用配置

### 步骤 1：准备数据模板

确保项目中存在 `data/print_layouts.json`。如果是首次部署，请从 `.example.json` 复制一份空模板：

```bash
cp data/print_layouts.example.json data/print_layouts.json
```

### 步骤 2：备份当前配置（可选）

如果你已经有正在使用的业务数据，建议在修改前备份：

```bash
cp data/print_layouts.json data/print_layouts.json.backup
```

### 步骤 3：编辑配置文件

打开 `data/print_layouts.json`，为需要限制的流程添加 `permissions` 字段。

**示例：为表单添加权限**

找到对应的流程配置：

```json
{
  "PROC-EXAMPLE-FORM-A": {
    "name": "示例表单 A",
    "base_pdf": "",
    "use_template": false,
    "orientation": "p",
    "items": [...]
  }
}
```

在同级添加 `permissions` 字段：

```json
{
  "PROC-EXAMPLE-FORM-A": {
    "name": "示例表单 A",
    "permissions": {
      "allowed_depts": ["测试部", "管理层"]
    },
    "base_pdf": "",
    "use_template": false,
    "orientation": "p",
    "items": [...]
  }
}
```

### 步骤 4：验证与测试

1. 确保修改后的 JSON 格式正确无误。
2. 使用不同部门的用户账号登录钉钉，访问打印门户。
3. 验证表单列表是否按照权限设置正确展示/隐藏。

## 常见问题

### Q1: 如何查看所有可用的部门名称？

可以访问后台的 `人员管理` 页面，查看当前同步下来的所有部门名称。

### Q2: 配置后没有生效怎么办？

1. 检查 JSON 格式是否正确（是否漏了逗号或者引号）。
2. 确认部门名称与 `users.json` 中的部门名称**完全一致**。
3. 刷新浏览器页面（清除缓存）。
4. 检查测试用户是否被成功同步到了 `users.json` 中。

### Q3: 如何临时开放所有流程？

直接删除或注释掉 `permissions` 字段即可：

```json
{
  "PROC-EXAMPLE-FORM-A": {
    "name": "示例表单 A",
    // "permissions": {
    //   "allowed_depts": ["部门A"]
    // },
    "base_pdf": "..."
  }
}
```

### Q4: 管理层需要看到所有流程怎么办？

在每个流程的 `allowed_depts` 数组中都加上 "管理层" 或对应的部门名称即可。

## 部门名称速查表示例

配置时，必须使用钉钉组织架构中的**精确名称**，例如：

| 业务领域 | 示例部门名称 |
|---------|---------|
| 管理层 | 总经办、董事会 |
| 研发 | 研发一部、研发二部、测试部 |
| 销售 | 销售中心、大客户部 |
| 生产 | 生产车间、品保部 |
| 后勤 | 人事部、财务部、行政部 |

## 下一步

1. 根据实际业务需求选择合适的配置方案。
2. 在测试环境中先行验证权限效果。
3. 逐步为线上流程配置权限。
