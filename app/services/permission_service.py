from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional


class PermissionService:
    """
    权限控制服务（基于钉钉数据）
    
    使用 users.json 中的钉钉数据进行权限判断
    结合 business_permissions.json 中的业务权限配置
    """
    
    def __init__(self, cfg):
        self.cfg = cfg
        self.users_file = cfg.base_dir / "data" / "users.json"
        self.permissions_file = cfg.base_dir / "data" / "business_permissions.json"
        
        # 加载钉钉数据
        self.dingtalk_data = self._load_dingtalk_data()
        self.users = self._build_users_dict()
        self.departments = self._build_departments_dict()
        
        # 加载业务权限配置
        self.business_permissions = self._load_business_permissions()
    
    def _load_dingtalk_data(self) -> Dict[str, Any]:
        """加载钉钉数据"""
        if self.users_file.exists():
            return json.loads(self.users_file.read_text(encoding="utf-8"))
        return {"users": [], "departments": []}
    
    def _build_users_dict(self) -> Dict[str, Dict[str, Any]]:
        """构建用户字典 {userid: user_info}"""
        users_list = self.dingtalk_data.get("users", [])
        return {user["userid"]: user for user in users_list}
    
    def _build_departments_dict(self) -> Dict[str, Dict[str, Any]]:
        """构建部门字典 {dept_id: dept_info}"""
        depts_list = self.dingtalk_data.get("departments", [])
        return {str(dept["dept_id"]): dept for dept in depts_list}
    
    def _load_business_permissions(self) -> Dict[str, Any]:
        """加载业务权限配置"""
        if self.permissions_file.exists():
            return json.loads(self.permissions_file.read_text(encoding="utf-8"))
        
        # 默认配置
        default_config = {
            "system_admins": [],
            "template_permissions": {},
            "default_rules": {
                "can_view_own": True,
                "dept_manager_can_view_dept": True,
                "admin_can_view_all": True
            }
        }
        
        # 创建默认配置文件
        self.permissions_file.parent.mkdir(parents=True, exist_ok=True)
        self.permissions_file.write_text(
            json.dumps(default_config, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        return default_config
    
    def reload(self):
        """重新加载所有配置"""
        self.dingtalk_data = self._load_dingtalk_data()
        self.users = self._build_users_dict()
        self.departments = self._build_departments_dict()
        self.business_permissions = self._load_business_permissions()
    
    # ========== 用户信息查询 ==========
    
    def get_user_info(self, userid: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        return self.users.get(userid)
    
    def get_user_dept_id(self, userid: str) -> str:
        """获取用户部门 ID"""
        user = self.users.get(userid, {})
        return user.get("dept_id", "")
    
    def get_user_dept_name(self, userid: str) -> str:
        """获取用户部门名称"""
        user = self.users.get(userid, {})
        return user.get("dept_name", "")
    
    def is_dept_manager(self, userid: str) -> bool:
        """检查是否是部门主管（从钉钉数据）"""
        user = self.users.get(userid, {})
        return user.get("is_dept_manager", False)
    
    def get_managed_depts(self, userid: str) -> List[str]:
        """获取用户管理的部门列表"""
        user = self.users.get(userid, {})
        return user.get("managed_depts", [])
    
    def is_system_admin(self, userid: str) -> bool:
        """检查是否是系统管理员"""
        return userid in self.business_permissions.get("system_admins", [])
    
    # ========== 权限判断 ==========
    
    def can_view_template(self, userid: str, p_code: str) -> bool:
        """
        检查用户是否可以查看模板
        
        判断逻辑:
        1. 系统管理员可以看所有
        2. 检查模板权限配置
        3. 没有配置权限，默认可见
        """
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
        """
        检查用户是否可以查看审批实例
        
        判断逻辑:
        1. 系统管理员可以看所有
        2. 自己提交的可以看
        3. 部门主管可以看部门成员的
        4. 检查模板的额外查看者配置
        """
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
    
    def filter_instances(self, userid: str, instances: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤审批实例列表，只返回用户有权限查看的
        
        Args:
            userid: 用户 ID
            instances: 审批实例列表
        
        Returns:
            用户有权限查看的审批实例列表
        """
        return [
            instance for instance in instances
            if self.can_view_instance(userid, instance)
        ]
    
    # ========== 部门信息查询 ==========
    
    def get_dept_info(self, dept_id: str) -> Optional[Dict[str, Any]]:
        """获取部门信息"""
        return self.departments.get(str(dept_id))
    
    def get_dept_name(self, dept_id: str) -> str:
        """获取部门名称"""
        dept = self.departments.get(str(dept_id), {})
        return dept.get("name", "")
    
    def get_dept_members(self, dept_id: str) -> List[Dict[str, Any]]:
        """获取部门成员列表"""
        return [
            user for user in self.users.values()
            if user.get("dept_id") == str(dept_id)
        ]
    
    # ========== 统计信息 ==========
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        managers = [u for u in self.users.values() if u.get("is_dept_manager")]
        admins = self.business_permissions.get("system_admins", [])
        
        return {
            "total_users": len(self.users),
            "total_departments": len(self.departments),
            "total_managers": len(managers),
            "total_admins": len(admins),
            "last_sync": self.dingtalk_data.get("last_sync", "未知")
        }
