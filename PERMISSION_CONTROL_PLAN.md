================================================================================
🔐 权限控制系统设计方案
================================================================================

## 📋 需求分析

### 核心需求
1. **用户只能看到自己提交的审批**（默认）
2. **部门主管可以看到部门成员的审批**（可配置）
3. **模板的显示和使用权限控制**（可配置）
4. **灵活的权限配置**（后台管理）

### 权限层级
```
Level 1: 普通用户 - 只能看自己的审批
Level 2: 部门主管 - 可以看部门成员的审批
Level 3: 管理员 - 可以看所有审批
```

================================================================================
## 🏗️ 系统架构设计
================================================================================

### 1. 数据结构设计

#### 1.1 用户权限配置 (data/user_permissions.json)
```json
{
  "users": {
    "userid001": {
      "role": "admin",
      "can_view_all": true,
      "can_manage_templates": true,
      "departments": ["部门A", "部门B"]
    },
    "userid002": {
      "role": "dept_manager",
      "can_view_dept": true,
      "departments": ["部门A"]
    },
    "userid003": {
      "role": "user",
      "can_view_dept": false,
      "departments": []
    }
  },
  "roles": {
    "admin": {
      "name": "管理员",
      "can_view_all": true,
      "can_manage_templates": true,
      "can_manage_users": true
    },
    "dept_manager": {
      "name": "部门主管",
      "can_view_dept": true,
      "can_manage_templates": false,
      "can_manage_users": false
    },
    "user": {
      "name": "普通用户",
      "can_view_dept": false,
      "can_manage_templates": false,
      "can_manage_users": false
    }
  }
}
```

#### 1.2 模板权限配置 (data/template_permissions.json)
```json
{
  "PROC-XXX-XXX": {
    "name": "设计图纸变更通知单",
    "visible_to": {
      "type": "departments",
      "departments": ["设计部", "技术部"],
      "users": ["userid001", "userid002"]
    },
    "can_submit": {
      "type": "departments",
      "departments": ["设计部"],
      "users": []
    },
    "viewers": {
      "type": "role",
      "roles": ["dept_manager", "admin"],
      "users": []
    }
  }
}
```

#### 1.3 部门配置 (data/departments.json)
```json
{
  "departments": {
    "设计部": {
      "dept_id": "123456",
      "managers": ["userid001", "userid002"],
      "members": ["userid003", "userid004"]
    },
    "技术部": {
      "dept_id": "123457",
      "managers": ["userid005"],
      "members": ["userid006", "userid007"]
    }
  }
}
```

================================================================================
## 🔧 技术实现
================================================================================

### 2. 权限控制器 (app/services/permission_service.py)

```python
class PermissionService:
    """权限控制服务"""
    
    def __init__(self, cfg):
        self.cfg = cfg
        self.user_permissions = self._load_user_permissions()
        self.template_permissions = self._load_template_permissions()
        self.departments = self._load_departments()
    
    def can_view_template(self, userid: str, p_code: str) -> bool:
        """检查用户是否可以查看模板"""
        # 1. 检查用户角色
        user_role = self.get_user_role(userid)
        if user_role == "admin":
            return True
        
        # 2. 检查模板权限配置
        template_perm = self.template_permissions.get(p_code)
        if not template_perm:
            return True  # 没有配置权限，默认可见
        
        # 3. 检查部门权限
        user_dept = self.get_user_department(userid)
        visible_depts = template_perm.get("visible_to", {}).get("departments", [])
        if user_dept in visible_depts:
            return True
        
        # 4. 检查用户白名单
        visible_users = template_perm.get("visible_to", {}).get("users", [])
        if userid in visible_users:
            return True
        
        return False
    
    def can_view_instance(self, userid: str, instance: dict) -> bool:
        """检查用户是否可以查看审批实例"""
        # 1. 管理员可以看所有
        user_role = self.get_user_role(userid)
        if user_role == "admin":
            return True
        
        # 2. 自己提交的可以看
        if instance.get("originator_userid") == userid:
            return True
        
        # 3. 部门主管可以看部门成员的
        if user_role == "dept_manager":
            user_dept = self.get_user_department(userid)
            instance_user_dept = self.get_user_department(
                instance.get("originator_userid")
            )
            if user_dept == instance_user_dept:
                return True
        
        # 4. 检查模板的查看者配置
        p_code = instance.get("p_code")
        template_perm = self.template_permissions.get(p_code)
        if template_perm:
            viewers = template_perm.get("viewers", {})
            viewer_roles = viewers.get("roles", [])
            if user_role in viewer_roles:
                return True
            
            viewer_users = viewers.get("users", [])
            if userid in viewer_users:
                return True
        
        return False
    
    def get_user_role(self, userid: str) -> str:
        """获取用户角色"""
        user_perm = self.user_permissions.get("users", {}).get(userid)
        if user_perm:
            return user_perm.get("role", "user")
        return "user"
    
    def get_user_department(self, userid: str) -> str:
        """获取用户部门"""
        # 从钉钉 API 获取或从缓存获取
        pass
    
    def is_dept_manager(self, userid: str, dept_name: str) -> bool:
        """检查用户是否是部门主管"""
        dept = self.departments.get("departments", {}).get(dept_name)
        if dept:
            return userid in dept.get("managers", [])
        return False
```

### 3. API 修改

#### 3.1 获取模板列表 (app/routes/portal.py)
```python
@portal_bp.route("/api/get_templates")
def get_templates():
    auth_code = request.args.get("code") or ""
    
    try:
        ding = _ding()
        userid = ding.get_userid_by_auth_code(auth_code)
    except DingTalkError:
        return jsonify({"errcode": 1, "errmsg": "身份校验失败"})
    
    cfg = _cfg()
    perm_service = PermissionService(cfg)  # 新增
    
    # Load templates
    templates = []
    for p_code, layout in designer_layouts.items():
        # 权限检查
        if not perm_service.can_view_template(userid, p_code):
            continue  # 跳过没有权限的模板
        
        templates.append({
            "p_code": p_code,
            "name": layout.get("name", p_code),
            "orientation": layout.get("orientation", "p"),
        })
    
    return jsonify({
        "errcode": 0,
        "templates": templates,
        "user_info": {...}
    })
```

#### 3.2 获取审批列表 (app/routes/portal.py)
```python
@portal_bp.route("/api/get_template_instances")
def get_template_instances():
    # ... 获取 userid 和 p_code ...
    
    cfg = _cfg()
    perm_service = PermissionService(cfg)  # 新增
    
    # 获取审批列表
    ins_ids = ding.list_process_instance_ids(p_code, userid, ...)
    
    my_list = []
    for ins_id in ins_ids:
        instance = ding.get_process_instance(ins_id)
        
        # 权限检查
        if not perm_service.can_view_instance(userid, instance):
            continue  # 跳过没有权限的审批
        
        my_list.append({...})
    
    return jsonify({
        "errcode": 0,
        "list": my_list,
        ...
    })
```

================================================================================
## 🎨 后台管理界面
================================================================================

### 4. 权限管理页面

#### 4.1 用户权限管理 (/admin/permissions/users)
```
┌─────────────────────────────────────────────────────┐
│ 用户权限管理                                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 搜索: [_____________] [搜索]                         │
│                                                      │
│ ┌──────────┬──────────┬──────────┬──────────┐      │
│ │ 用户     │ 部门     │ 角色     │ 操作     │      │
│ ├──────────┼──────────┼──────────┼──────────┤      │
│ │ 张三     │ 设计部   │ 部门主管 │ [编辑]   │      │
│ │ 李四     │ 设计部   │ 普通用户 │ [编辑]   │      │
│ │ 王五     │ 技术部   │ 管理员   │ [编辑]   │      │
│ └──────────┴──────────┴──────────┴──────────┘      │
│                                                      │
│ [添加用户权限]                                       │
└─────────────────────────────────────────────────────┘
```

#### 4.2 模板权限管理 (/admin/permissions/templates)
```
┌─────────────────────────────────────────────────────┐
│ 模板权限管理                                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 模板: [设计图纸变更通知单 ▼]                        │
│                                                      │
│ ┌─ 可见范围 ─────────────────────────────────┐     │
│ │ ☑ 所有人可见                                │     │
│ │ ☐ 指定部门: [设计部] [技术部] [+添加]      │     │
│ │ ☐ 指定用户: [张三] [李四] [+添加]          │     │
│ └─────────────────────────────────────────────┘     │
│                                                      │
│ ┌─ 提交权限 ─────────────────────────────────┐     │
│ │ ☑ 所有人可提交                              │     │
│ │ ☐ 指定部门: [设计部] [+添加]               │     │
│ │ ☐ 指定用户: [+添加]                        │     │
│ └─────────────────────────────────────────────┘     │
│                                                      │
│ ┌─ 查看权限 ─────────────────────────────────┐     │
│ │ ☑ 仅提交人可查看                            │     │
│ │ ☑ 部门主管可查看部门成员的审批              │     │
│ │ ☐ 指定角色: [管理员] [+添加]               │     │
│ │ ☐ 指定用户: [+添加]                        │     │
│ └─────────────────────────────────────────────┘     │
│                                                      │
│ [保存] [取消]                                        │
└─────────────────────────────────────────────────────┘
```

#### 4.3 部门管理 (/admin/permissions/departments)
```
┌─────────────────────────────────────────────────────┐
│ 部门管理                                             │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌──────────┬──────────┬──────────┬──────────┐      │
│ │ 部门名称 │ 部门主管 │ 成员数   │ 操作     │      │
│ ├──────────┼──────────┼──────────┼──────────┤      │
│ │ 设计部   │ 张三     │ 15       │ [编辑]   │      │
│ │ 技术部   │ 王五     │ 20       │ [编辑]   │      │
│ │ 行政部   │ 赵六     │ 8        │ [编辑]   │      │
│ └──────────┴──────────┴──────────┴──────────┘      │
│                                                      │
│ [同步钉钉部门]                                       │
└─────────────────────────────────────────────────────┘
```

================================================================================
## 📊 权限判断流程
================================================================================

### 5. 权限判断流程图

```
用户访问打印门户
    ↓
获取用户信息（userid, 部门, 角色）
    ↓
加载模板列表
    ↓
┌─────────────────────────────────┐
│ 对每个模板进行权限检查:          │
│                                  │
│ 1. 是否是管理员？                │
│    是 → 显示                     │
│    否 → 继续检查                 │
│                                  │
│ 2. 模板是否配置了可见范围？      │
│    否 → 显示（默认可见）         │
│    是 → 继续检查                 │
│                                  │
│ 3. 用户部门是否在可见范围？      │
│    是 → 显示                     │
│    否 → 继续检查                 │
│                                  │
│ 4. 用户是否在白名单？            │
│    是 → 显示                     │
│    否 → 隐藏                     │
└─────────────────────────────────┘
    ↓
显示有权限的模板列表
    ↓
用户点击模板
    ↓
加载审批列表
    ↓
┌─────────────────────────────────┐
│ 对每个审批进行权限检查:          │
│                                  │
│ 1. 是否是管理员？                │
│    是 → 显示                     │
│    否 → 继续检查                 │
│                                  │
│ 2. 是否是提交人？                │
│    是 → 显示                     │
│    否 → 继续检查                 │
│                                  │
│ 3. 是否是部门主管？              │
│    是 → 检查是否同部门           │
│        是 → 显示                 │
│        否 → 继续检查             │
│    否 → 继续检查                 │
│                                  │
│ 4. 模板是否配置了查看者？        │
│    是 → 检查角色/用户            │
│        匹配 → 显示               │
│        不匹配 → 隐藏             │
│    否 → 隐藏                     │
└─────────────────────────────────┘
    ↓
显示有权限的审批列表
```

================================================================================
## 🚀 实施步骤
================================================================================

### 6. 分阶段实施

#### 阶段 1: 基础权限控制（1-2 天）
- [ ] 创建 PermissionService 类
- [ ] 实现基础权限判断逻辑
- [ ] 修改 API 接口集成权限检查
- [ ] 测试基础功能

#### 阶段 2: 数据结构和配置（1 天）
- [ ] 设计权限配置文件结构
- [ ] 创建默认配置文件
- [ ] 实现配置文件读写
- [ ] 测试配置加载

#### 阶段 3: 后台管理界面（2-3 天）
- [ ] 创建用户权限管理页面
- [ ] 创建模板权限管理页面
- [ ] 创建部门管理页面
- [ ] 实现权限配置保存

#### 阶段 4: 钉钉集成（1 天）
- [ ] 同步钉钉部门信息
- [ ] 同步钉钉用户信息
- [ ] 自动识别部门主管
- [ ] 测试同步功能

#### 阶段 5: 测试和优化（1 天）
- [ ] 全面测试各种权限场景
- [ ] 性能优化
- [ ] 文档编写
- [ ] 部署上线

================================================================================
## 💡 最佳实践建议
================================================================================

### 7. 安全建议

1. **默认拒绝原则**
   - 没有明确授权的，默认拒绝访问
   - 宁可多一步授权，也不要泄露数据

2. **最小权限原则**
   - 用户只能看到必要的数据
   - 部门主管只能看本部门的数据

3. **审计日志**
   - 记录所有权限检查
   - 记录权限配置变更
   - 便于追溯和审计

4. **缓存策略**
   - 权限配置可以缓存
   - 定期刷新或手动刷新
   - 避免频繁读取文件

5. **性能优化**
   - 批量权限检查
   - 避免重复查询
   - 使用索引加速查找

================================================================================
## 📝 配置示例
================================================================================

### 8. 典型场景配置

#### 场景 1: 设计部门的变更通知单
```json
{
  "PROC-XXX-XXX": {
    "name": "设计图纸变更通知单",
    "visible_to": {
      "type": "departments",
      "departments": ["设计部", "技术部", "生产部"]
    },
    "can_submit": {
      "type": "departments",
      "departments": ["设计部"]
    },
    "viewers": {
      "type": "role",
      "roles": ["dept_manager", "admin"]
    }
  }
}
```
**说明**: 
- 设计部、技术部、生产部可以看到这个模板
- 只有设计部可以提交
- 部门主管和管理员可以查看所有审批

#### 场景 2: 财务报销单
```json
{
  "PROC-YYY-YYY": {
    "name": "财务报销单",
    "visible_to": {
      "type": "all"
    },
    "can_submit": {
      "type": "all"
    },
    "viewers": {
      "type": "departments",
      "departments": ["财务部"],
      "roles": ["admin"]
    }
  }
}
```
**说明**:
- 所有人可见和提交
- 只有财务部和管理员可以查看所有人的报销单
- 普通用户只能看自己的

================================================================================
## ✅ 总结
================================================================================

### 优势
1. ✅ 灵活的权限控制
2. ✅ 多层级权限支持
3. ✅ 易于配置和管理
4. ✅ 安全可靠
5. ✅ 可扩展性强

### 下一步
1. 确认方案是否符合需求
2. 开始实施阶段 1
3. 逐步完善功能

================================================================================
