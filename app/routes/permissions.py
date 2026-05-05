from __future__ import annotations

from flask import Blueprint, render_template, request, jsonify, current_app
import json

from app.services.permission_service import PermissionService
from app.config import load_config

permissions_bp = Blueprint("permissions", __name__, url_prefix="/admin/permissions")


def _perm() -> PermissionService:
    """获取权限服务实例"""
    cfg = load_config()
    return PermissionService(cfg)


@permissions_bp.route("/")
def index():
    """权限管理主页"""
    return render_template("permissions/index.html")


@permissions_bp.route("/admins")
def admins():
    """系统管理员配置页面"""
    return render_template("permissions/admins.html")


@permissions_bp.route("/templates")
def templates():
    """模板权限配置页面"""
    return render_template("permissions/templates.html")


@permissions_bp.route("/managers")
def managers():
    """部门主管查看页面"""
    return render_template("permissions/managers.html")


# ========== API 接口 ==========

@permissions_bp.route("/api/stats")
def api_stats():
    """获取权限统计信息"""
    try:
        perm = _perm()
        stats = perm.get_stats()
        return jsonify({"errcode": 0, "data": stats})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/admins/list")
def api_admins_list():
    """获取系统管理员列表"""
    try:
        perm = _perm()
        admin_userids = perm.business_permissions.get("system_admins", [])
        
        admins = []
        for userid in admin_userids:
            user_info = perm.get_user_info(userid)
            if user_info:
                admins.append({
                    "userid": userid,
                    "name": user_info.get("name"),
                    "dept_name": user_info.get("dept_name"),
                    "mobile": user_info.get("mobile", "")[:3] + "****" + user_info.get("mobile", "")[-4:] if user_info.get("mobile") else ""
                })
        
        return jsonify({"errcode": 0, "data": admins})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/admins/add", methods=["POST"])
def api_admins_add():
    """添加系统管理员"""
    try:
        data = request.get_json()
        userid = data.get("userid")
        
        if not userid:
            return jsonify({"errcode": 1, "errmsg": "缺少用户ID"})
        
        perm = _perm()
        
        # 检查用户是否存在
        user_info = perm.get_user_info(userid)
        if not user_info:
            return jsonify({"errcode": 1, "errmsg": "用户不存在"})
        
        # 添加到管理员列表
        admin_userids = perm.business_permissions.get("system_admins", [])
        if userid in admin_userids:
            return jsonify({"errcode": 1, "errmsg": "该用户已是管理员"})
        
        admin_userids.append(userid)
        perm.business_permissions["system_admins"] = admin_userids
        
        # 保存配置
        perm.permissions_file.write_text(
            json.dumps(perm.business_permissions, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        return jsonify({"errcode": 0, "errmsg": "添加成功"})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/admins/remove", methods=["POST"])
def api_admins_remove():
    """移除系统管理员"""
    try:
        data = request.get_json()
        userid = data.get("userid")
        
        if not userid:
            return jsonify({"errcode": 1, "errmsg": "缺少用户ID"})
        
        perm = _perm()
        
        # 从管理员列表移除
        admin_userids = perm.business_permissions.get("system_admins", [])
        if userid not in admin_userids:
            return jsonify({"errcode": 1, "errmsg": "该用户不是管理员"})
        
        admin_userids.remove(userid)
        perm.business_permissions["system_admins"] = admin_userids
        
        # 保存配置
        perm.permissions_file.write_text(
            json.dumps(perm.business_permissions, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        return jsonify({"errcode": 0, "errmsg": "移除成功"})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/users/search")
def api_users_search():
    """搜索用户"""
    try:
        keyword = request.args.get("keyword", "").strip()
        
        if not keyword:
            return jsonify({"errcode": 1, "errmsg": "请输入搜索关键词"})
        
        perm = _perm()
        
        # 搜索用户
        results = []
        for userid, user_info in perm.users.items():
            name = user_info.get("name", "")
            mobile = user_info.get("mobile", "")
            dept_name = user_info.get("dept_name", "")
            
            if keyword.lower() in name.lower() or keyword in mobile:
                results.append({
                    "userid": userid,
                    "name": name,
                    "dept_name": dept_name,
                    "mobile": mobile[:3] + "****" + mobile[-4:] if mobile else ""
                })
                
                if len(results) >= 20:  # 限制返回数量
                    break
        
        return jsonify({"errcode": 0, "data": results})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/managers/list")
def api_managers_list():
    """获取部门主管列表"""
    try:
        perm = _perm()
        
        managers = []
        for userid, user_info in perm.users.items():
            if user_info.get("is_dept_manager"):
                managed_dept_names = []
                for dept_id in user_info.get("managed_depts", []):
                    dept_info = perm.get_dept_info(dept_id)
                    if dept_info:
                        managed_dept_names.append(dept_info.get("name"))
                
                managers.append({
                    "userid": userid,
                    "name": user_info.get("name"),
                    "dept_name": user_info.get("dept_name"),
                    "managed_depts": managed_dept_names
                })
        
        return jsonify({"errcode": 0, "data": managers})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/templates/list")
def api_templates_list():
    """获取模板列表"""
    try:
        cfg = load_config()
        
        # Load designer layouts
        designer_layouts = {}
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                # 只获取流程配置，排除 pdf_templates
                designer_layouts = {k: v for k, v in data.items() if k.startswith("PROC-")}
        
        templates = []
        for p_code, layout in designer_layouts.items():
            templates.append({
                "p_code": p_code,
                "name": layout.get("name", p_code),
                "orientation": layout.get("orientation", "p")
            })
        
        return jsonify({"errcode": 0, "data": templates})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/templates/permission/<p_code>")
def api_template_permission(p_code):
    """获取模板权限配置"""
    try:
        perm = _perm()
        template_perms = perm.business_permissions.get("template_permissions", {})
        template_perm = template_perms.get(p_code, {})
        
        return jsonify({"errcode": 0, "data": template_perm})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/templates/permission/<p_code>", methods=["POST"])
def api_template_permission_save(p_code):
    """保存模板权限配置"""
    try:
        data = request.get_json()
        
        perm = _perm()
        template_perms = perm.business_permissions.get("template_permissions", {})
        template_perms[p_code] = data
        perm.business_permissions["template_permissions"] = template_perms
        
        # 保存配置
        perm.permissions_file.write_text(
            json.dumps(perm.business_permissions, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        return jsonify({"errcode": 0, "errmsg": "保存成功"})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})


@permissions_bp.route("/api/departments/list")
def api_departments_list():
    """获取部门列表"""
    try:
        perm = _perm()
        
        departments = []
        for dept_id, dept_info in perm.departments.items():
            departments.append({
                "dept_id": dept_id,
                "name": dept_info.get("name"),
                "parent_id": dept_info.get("parent_id"),
                "member_count": dept_info.get("member_count", 0)
            })
        
        return jsonify({"errcode": 0, "data": departments})
    except Exception as e:
        return jsonify({"errcode": 1, "errmsg": str(e)})
