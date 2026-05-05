================================================================================
🔐 权限控制系统设计方案 V2（钉钉集成版）
================================================================================

## 🎯 核心理念

**与钉钉深度集成，而不是独立的权限系统**

- ✅ 使用钉钉的组织架构（部门、人员）
- ✅ 使用钉钉的角色体系（部门主管、普通员工）
- ✅ 只在钉钉基础上添加业务权限配置
- ✅ 自动同步钉钉数据，保持一致性

================================================================================
## 🏗️ 系统架构设计（钉钉集成版）
================================================================================

### 1. 数据来源

```
┌─────────────────────────────────────────────────────┐
│ 钉钉 API（主数据源）                                 │
├─────────────────────────────────────────────────────┤
│ - 用户信息（userid, name, dept）                    │
│ - 部门信息（dept_id, name, parent_id）              │
│ - 部门主管（通过 API 获取）                          │
│ - 组织架构（树形结构）                               │
└─────────────────────────────────────────────────────┘
                    ↓ 同步
┌─────────────────────────────────────────────────────┐
│ 本地缓存（data/dingtalk_cache.json）                │
├─────────────────────────────────────────────────────┤
│ - 定期同步（每天一次）                               │
│ - 手动同步（后台按钮）                               │
│ - 加速查询（避免频繁调用钉钉 API）                  │
└─────────────────────────────────────────────────────┘
                    ↓ 使用
┌─────────────────────────────────────────────────────┐
│ 业务权限配置（data/business_permissions.json）      │
├─────────────────────────────────────────────────────┤
│ - 只配置业务相关的权限                               │
│ - 基于钉钉的组织架构                                 │
│ - 不重复存储钉钉已有的数据                           │
└─────────────────────────────────────────────────────┘
```

---

## 📊 数据结构设计

### 1.1 钉钉数据缓存 (data/dingtalk_cache.json)

```json
{
  "last_sync": "2026-05-05 12:00:00",
  "users": {
    "userid001": {
      "name": "张三",
      "dept_id": "123456",
      "dept_name": "设计部",
      "mobile": "13800138000",
      "is_dept_manager": true,
      "managed_depts": ["123456"]
    },
    "userid002": {
      "name": "李四",
      "dept_id": "123456",
      "dept_name": "设计部",
      "mobile": "13800138001",
      "is_dept_manager": false,
      "managed_depts": []
    }
  },
  "departments": {
    "123456": {
      "name": "设计部",
      "parent_id": "1",
      "manager_userids": ["userid001"],
      "member_count": 15
    },
    "123457": {
      "name": "技术部",
      "parent_id": "1",
      "manager_userids": ["userid003"],
      "member_count": 20
    }
  }
}
```

**说明**：
- 从钉钉 API 同步
- 包含用户、部门、主管关系
- 定期自动更新

---

### 1.2 业务权限配置 (data/business_permissions.json)

```json
{
  "system_admins": [
    "userid001",
    "userid005"
  ],
  "template_permissions": {
    "PROC-XXX-XXX": {
      "name": "设计图纸变更通知单",
      "visible_to": {
        "type": "departments",
        "dept_ids": ["123456", "123457", "123458"]
      },
      "can_submit": {
        "type": "departments",
        "dept_ids": ["123456"]
      },
      "extra_viewers": {
        "type": "dept_managers",
        "scope": "all"
      }
    },
    "PROC-YYY-YYY": {
      "name": "财务报销单",
      "visible_to": {
        "type": "all"
      },
      "can_submit": {
        "type": "all"
      },
      "extra_viewers": {
        "type": "departments",
        "dept_ids": ["123459"]
      }
    }
  },
  "default_rules": {
    "can_view_own": true,
    "dept_manager_can_view_dept": true,
    "admin_can_view_all": true
  }
}
```

**说明**：
- 只配置业务权限
- 使用钉钉的 dept_id 和 userid
- 不重复存储钉钉数据

---

## 🔧 技术实现

### 2. 钉钉数据同步服务 (app/services/dingtalk_sync_service.py)

```python
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Any

from app.services.dingtalk_service import DingTalkService, DingTalkError


class DingTalkSyncService:
    """钉钉数据同步服务"""
    
    def __init__(self, cfg, ding_service: DingTalkService):
        self.cfg = cfg
        self.ding = ding_service
        self.cache_file = cfg.base_dir / "data" / "dingtalk_cache.json"
    
    def sync_all(self) -> Dict[str, Any]:
        """同步所有钉钉数据"""
        print("开始同步钉钉数据...")
        
        # 1. 同步部门列表
        departments = self._sync_departments()
        print(f"✅ 同步了 {len(departments)} 个部门")
        
        # 2. 同步用户列表
        users = self._sync_users(departments)
        print(f"✅ 同步了 {len(users)} 个用户")
        
        # 3. 识别部门主管
        self._identify_dept_managers(users, departments)
        print(f"✅ 识别了部门主管")
        
        # 4. 保存缓存
        cache_data = {
            "last_sync": time.strftime("%Y-%m-%d %H:%M:%S"),
            "users": users,
            "departments": departments
        }
        self._save_cache(cache_data)
        print(f"✅ 缓存已保存")
        
        return cache_data
    
    def _sync_departments(self) -> Dict[str, Any]:
        """同步部门列表"""
        departments = {}
        
        # 调用钉钉 API 获取部门列表
        # GET /topapi/v2/department/listsub
        token = self.ding.get_access_token()
        
        # 递归获取所有部门
        def get_dept_tree(parent_id=1):
            try:
                resp = self.ding.session.post(
                    self.ding._url("/topapi/v2/department/listsub"),
                    params={"access_token": token},
                    json={"dept_id": parent_id},
                    timeout=self.ding.cfg.request_timeout_seconds,
                )
                data = resp.json()
                
                if data.get("errcode") == 0:
                    dept_list = data.get("result", [])
                    for dept in dept_list:
                        dept_id = str(dept.get("dept_id"))
                        departments[dept_id] = {
                            "name": dept.get("name"),
                            "parent_id": str(dept.get("parent_id")),
                            "manager_userids": [],
                            "member_count": 0
                        }
                        # 递归获取子部门
                        get_dept_tree(dept_id)
            except Exception as e:
                print(f"获取部门失败: {e}")
        
        get_dept_tree()
        return departments
    
    def _sync_users(self, departments: Dict[str, Any]) -> Dict[str, Any]:
        """同步用户列表"""
        users = {}
        
        # 遍历每个部门，获取部门成员
        for dept_id, dept_info in departments.items():
            try:
                # 调用钉钉 API 获取部门成员
                # POST /topapi/v2/user/list
                token = self.ding.get_access_token()
                resp = self.ding.session.post(
                    self.ding._url("/topapi/v2/user/list"),
                    params={"access_token": token},
                    json={
                        "dept_id": int(dept_id),
                        "cursor": 0,
                        "size": 100
                    },
                    timeout=self.ding.cfg.request_timeout_seconds,
                )
                data = resp.json()
                
                if data.get("errcode") == 0:
                    user_list = data.get("result", {}).get("list", [])
                    dept_info["member_count"] = len(user_list)
                    
                    for user in user_list:
                        userid = user.get("userid")
                        users[userid] = {
                            "name": user.get("name"),
                            "dept_id": dept_id,
                            "dept_name": dept_info["name"],
                            "mobile": user.get("mobile", ""),
                            "is_dept_manager": False,
                            "managed_depts": []
                        }
            except Exception as e:
                print(f"获取部门 {dept_id} 成员失败: {e}")
        
        return users
    
    def _identify_dept_managers(self, users: Dict[str, Any], departments: Dict[str, Any]):
        """识别部门主管"""
        for dept_id, dept_info in departments.items():
            try:
                # 调用钉钉 API 获取部门详情
                # POST /topapi/v2/department/get
                token = self.ding.get_access_token()
                resp = self.ding.session.post(
                    self.ding._url("/topapi/v2/department/get"),
                    params={"access_token": token},
                    json={"dept_id": int(dept_id)},
                    timeout=self.ding.cfg.request_timeout_seconds,
                )
                data = resp.json()
                
                if data.get("errcode") == 0:
                    result = data.get("result", {})
                    # 获取部门主管 userid
                    dept_manager_userid_list = result.get("dept_manager_userid_list", [])
                    
                    dept_info["manager_userids"] = dept_manager_userid_list
                    
                    # 标记用户为部门主管
                    for userid in dept_manager_userid_list:
                        if userid in users:
                            users[userid]["is_dept_manager"] = True
                            users[userid]["managed_depts"].append(dept_id)
            except Exception as e:
                print(f"获取部门 {dept_id} 详情失败: {e}")
    
    def _save_cache(self, cache_data: Dict[str, Any]):
        """保存缓存"""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache_file.write_text(
            json.dumps(cache_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def load_cache(self) -> Dict[str, Any]:
        """加载缓存"""
        if self.cache_file.exists():
            return json.loads(self.cache_file.read_text(encoding="utf-8"))
        return {"users": {}, "departments": {}}
    
    def is_cache_expired(self, max_age_hours: int = 24) -> bool:
        """检查缓存是否过期"""
        cache = self.load_cache()
        last_sync = cache.get("last_sync")
        if not last_sync:
            return True
        
        last_sync_time = time.mktime(time.strptime(last_sync, "%Y-%m-%d %H:%M:%S"))
        now = time.time()
        age_hours = (now - last_sync_time) / 3600
        
        return age_hours > max_age_hours
```

---

### 3. 权限控制服务 (app/services/permission_service.py)

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List

from app.services.dingtalk_sync_service import DingTalkSyncService


class PermissionService:
    """权限控制服务（基于钉钉数据）"""
    
    def __init__(self, cfg, sync_service: DingTalkSyncService):
        self.cfg = cfg
        self.sync_service = sync_service
        self.permissions_file = cfg.base_dir / "data" / "business_permissions.json"
        
        # 加载钉钉缓存数据
        self.dingtalk_cache = sync_service.load_cache()
        self.users = self.dingtalk_cache.get("users", {})
        self.departments = self.dingtalk_cache.get("departments", {})
        
        # 加载业务权限配置
        self.business_permissions = self._load_business_permissions()
    
    def _load_business_permissions(self) -> Dict[str, Any]:
        """加载业务权限配置"""
        if self.permissions_file.exists():
            return json.loads(self.permissions_file.read_text(encoding="utf-8"))
        
        # 默认配置
        return {
            "system_admins": [],
            "template_permissions": {},
            "default_rules": {
                "can_view_own": True,
                "dept_manager_can_view_dept": True,
                "admin_can_view_all": True
            }
        }
    
    def is_system_admin(self, userid: str) -> bool:
        """检查是否是系统管理员"""
        return userid in self.business_permissions.get("system_admins", [])
    
    def is_dept_manager(self, userid: str) -> bool:
        """检查是否是部门主管（从钉钉数据）"""
        user = self.users.get(userid, {})
        return user.get("is_dept_manager", False)
    
    def get_user_dept_id(self, userid: str) -> str:
        """获取用户部门 ID（从钉钉数据）"""
        user = self.users.get(userid, {})
        return user.get("dept_id", "")
    
    def get_managed_depts(self, userid: str) -> List[str]:
        """获取用户管理的部门列表（从钉钉数据）"""
        user = self.users.get(userid, {})
        return user.get("managed_depts", [])
    
    def can_view_template(self, userid: str, p_code: str) -> bool:
        """检查用户是否可以查看模板"""
        # 1. 系统管理员可以看所有
        if self.is_system_admin(userid):
            return True
        
        # 2. 检查模板权限配置
        template_perms = self.business_permissions.get("template_permissions", {})
        template_perm = template_perms.get(p_code)
        
        if not template_perm:
            return True  # 没有配置权限，默认可见
        
        visible_to = template_perm.get("visible_to", {})
        visible_type = visible_to.get("type")
        
        # 3. 所有人可见
        if visible_type == "all":
            return True
        
        # 4. 指定部门可见
        if visible_type == "departments":
            user_dept_id = self.get_user_dept_id(userid)
            visible_dept_ids = visible_to.get("dept_ids", [])
            if user_dept_id in visible_dept_ids:
                return True
        
        # 5. 指定用户可见
        visible_userids = visible_to.get("userids", [])
        if userid in visible_userids:
            return True
        
        return False
    
    def can_view_instance(self, userid: str, instance: Dict[str, Any]) -> bool:
        """检查用户是否可以查看审批实例"""
        # 1. 系统管理员可以看所有
        if self.is_system_admin(userid):
            return True
        
        # 2. 自己提交的可以看
        originator_userid = instance.get("originator_userid")
        if originator_userid == userid:
            return True
        
        # 3. 部门主管可以看部门成员的
        default_rules = self.business_permissions.get("default_rules", {})
        if default_rules.get("dept_manager_can_view_dept", True):
            if self.is_dept_manager(userid):
                # 检查是否是同部门
                user_dept_id = self.get_user_dept_id(userid)
                originator_dept_id = self.get_user_dept_id(originator_userid)
                
                if user_dept_id == originator_dept_id:
                    return True
        
        # 4. 检查模板的额外查看者配置
        p_code = instance.get("p_code")
        template_perms = self.business_permissions.get("template_permissions", {})
        template_perm = template_perms.get(p_code)
        
        if template_perm:
            extra_viewers = template_perm.get("extra_viewers", {})
            viewer_type = extra_viewers.get("type")
            
            # 所有部门主管可以查看
            if viewer_type == "dept_managers":
                scope = extra_viewers.get("scope")
                if scope == "all" and self.is_dept_manager(userid):
                    return True
            
            # 指定部门可以查看
            if viewer_type == "departments":
                user_dept_id = self.get_user_dept_id(userid)
                viewer_dept_ids = extra_viewers.get("dept_ids", [])
                if user_dept_id in viewer_dept_ids:
                    return True
            
            # 指定用户可以查看
            viewer_userids = extra_viewers.get("userids", [])
            if userid in viewer_userids:
                return True
        
        return False
    
    def get_user_info(self, userid: str) -> Dict[str, Any]:
        """获取用户信息（从钉钉缓存）"""
        return self.users.get(userid, {})
    
    def get_dept_info(self, dept_id: str) -> Dict[str, Any]:
        """获取部门信息（从钉钉缓存）"""
        return self.departments.get(dept_id, {})
```

---

## 🎨 后台管理界面

### 4.1 钉钉数据同步页面 (/admin/sync/dingtalk)

```
┌─────────────────────────────────────────────────────┐
│ 钉钉数据同步                                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 上次同步时间: 2026-05-05 12:00:00                   │
│                                                      │
│ ┌─ 同步状态 ─────────────────────────────────┐     │
│ │ ✅ 部门: 25 个                              │     │
│ │ ✅ 用户: 156 个                             │     │
│ │ ✅ 部门主管: 8 个                           │     │
│ └─────────────────────────────────────────────┘     │
│                                                      │
│ [立即同步] [查看详情]                                │
│                                                      │
│ ⚙️ 自动同步设置:                                    │
│ ☑ 启用自动同步                                      │
│ 同步间隔: [24] 小时                                 │
│                                                      │
│ [保存设置]                                           │
└─────────────────────────────────────────────────────┘
```

### 4.2 系统管理员配置 (/admin/permissions/admins)

```
┌─────────────────────────────────────────────────────┐
│ 系统管理员配置                                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 当前管理员:                                          │
│                                                      │
│ ┌──────────┬──────────┬──────────┬──────────┐      │
│ │ 姓名     │ 部门     │ 手机号   │ 操作     │      │
│ ├──────────┼──────────┼──────────┼──────────┤      │
│ │ 张三     │ 设计部   │ 138****  │ [移除]   │      │
│ │ 王五     │ 技术部   │ 139****  │ [移除]   │      │
│ └──────────┴──────────┴──────────┴──────────┘      │
│                                                      │
│ 添加管理员:                                          │
│ 搜索用户: [_____________] [搜索]                     │
│                                                      │
│ 搜索结果:                                            │
│ ○ 李四 - 设计部 - 138**** [添加]                    │
│ ○ 赵六 - 行政部 - 137**** [添加]                    │
└─────────────────────────────────────────────────────┘
```

### 4.3 模板权限配置 (/admin/permissions/templates)

```
┌─────────────────────────────────────────────────────┐
│ 模板权限配置                                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 模板: [设计图纸变更通知单 ▼]                        │
│                                                      │
│ ┌─ 可见范围 ─────────────────────────────────┐     │
│ │ ☑ 所有人可见                                │     │
│ │ ☐ 指定部门:                                 │     │
│ │   [设计部 ×] [技术部 ×] [+添加部门]        │     │
│ └─────────────────────────────────────────────┘     │
│                                                      │
│ ┌─ 提交权限 ─────────────────────────────────┐     │
│ │ ☑ 所有人可提交                              │     │
│ │ ☐ 指定部门:                                 │     │
│ │   [设计部 ×] [+添加部门]                   │     │
│ └─────────────────────────────────────────────┘     │
│                                                      │
│ ┌─ 额外查看权限 ─────────────────────────────┐     │
│ │ ☑ 部门主管可查看本部门成员的审批            │     │
│ │ ☐ 所有部门主管可查看                        │     │
│ │ ☐ 指定部门可查看:                           │     │
│ │   [+添加部门]                               │     │
│ │ ☐ 指定用户可查看:                           │     │
│ │   [+添加用户]                               │     │
│ └─────────────────────────────────────────────┘     │
│                                                      │
│ [保存] [取消]                                        │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 实施步骤（优化版）

### 阶段 1: 钉钉数据同步（1 天）
- [ ] 创建 DingTalkSyncService 类
- [ ] 实现部门同步
- [ ] 实现用户同步
- [ ] 实现部门主管识别
- [ ] 测试同步功能

### 阶段 2: 权限控制服务（1 天）
- [ ] 创建 PermissionService 类
- [ ] 实现基于钉钉数据的权限判断
- [ ] 修改 API 集成权限检查
- [ ] 测试权限功能

### 阶段 3: 后台管理界面（2 天）
- [ ] 钉钉数据同步页面
- [ ] 系统管理员配置页面
- [ ] 模板权限配置页面
- [ ] 测试管理功能

### 阶段 4: 自动同步和优化（1 天）
- [ ] 实现定时自动同步
- [ ] 缓存优化
- [ ] 性能测试
- [ ] 部署上线

---

## ✅ 方案优势（V2）

1. ✅ **与钉钉深度集成** - 使用钉钉的组织架构
2. ✅ **数据自动同步** - 保持与钉钉一致
3. ✅ **简化配置** - 只配置业务权限
4. ✅ **易于维护** - 不需要手动维护人员列表
5. ✅ **灵活扩展** - 可以在钉钉基础上添加业务规则

---

## 📊 数据流程

```
钉钉 API
    ↓ 同步（每天一次）
本地缓存 (dingtalk_cache.json)
    ├─ 用户列表
    ├─ 部门列表
    └─ 主管关系
    ↓ 使用
业务权限配置 (business_permissions.json)
    ├─ 系统管理员
    ├─ 模板权限
    └─ 默认规则
    ↓ 判断
权限控制服务 (PermissionService)
    ├─ can_view_template()
    └─ can_view_instance()
    ↓ 应用
API 接口
    ├─ /api/get_templates
    └─ /api/get_template_instances
```

---

## 💡 关键改进

### V1 vs V2 对比

| 特性 | V1（独立权限） | V2（钉钉集成）⭐ |
|------|----------------|------------------|
| 数据来源 | 手动配置 | 钉钉 API 自动同步 |
| 组织架构 | 独立维护 | 使用钉钉组织架构 |
| 部门主管 | 手动配置 | 钉钉自动识别 |
| 数据一致性 | 容易脱钩 | 自动保持一致 |
| 维护成本 | 高 | 低 |
| 扩展性 | 一般 | 强 |

---

## 🎯 总结

### V2 方案的核心思想

**不重复造轮子，充分利用钉钉已有的能力**

1. **组织架构** - 直接使用钉钉的
2. **人员信息** - 直接使用钉钉的
3. **部门主管** - 直接使用钉钉的
4. **业务权限** - 只配置业务相关的

### 下一步

如果这个方案符合需求，我可以立即开始实施：
1. 先实现钉钉数据同步（1 天）
2. 再实现权限控制（1 天）
3. 最后实现后台管理（2 天）

总计 4-5 天完成。

================================================================================
