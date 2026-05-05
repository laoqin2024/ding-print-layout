from __future__ import annotations

import json
import time

from flask import Blueprint, current_app, jsonify, render_template, request

from app.services.dingtalk_service import DingTalkError, DingTalkService
from app.services.pdf_service import load_process_configs
from app.services.permission_service import PermissionService


portal_bp = Blueprint("portal_bp", __name__)


def _cfg():
    return current_app.extensions["app_cfg"]


def _perm() -> PermissionService:
    from app.config import load_config
    cfg = load_config()
    return PermissionService(cfg)


def _ding() -> DingTalkService:
    return current_app.extensions["dingtalk"]


@portal_bp.route("/")
def index():
    cfg = _cfg()
    return render_template("portal.html", corp_id=cfg.corp_id)


def _load_user_info(userid: str, cfg):
    """Load user info from users.json"""
    try:
        users_path = cfg.base_dir / "data" / "users.json"
        if users_path.exists():
            data = json.loads(users_path.read_text(encoding="utf-8"))
            users = data.get("users", [])
            for u in users:
                if u.get("userid") == userid:
                    return u
    except Exception:
        pass
    return None


def _check_process_permission(user_info, p_code, p_info):
    """Check if user has permission to view this process"""
    # Handle both old format (dict with zones) and new format (dict with items)
    # Also handle case where p_info might be a list or None
    if not isinstance(p_info, dict):
        # If p_info is not a dict, allow access by default
        return True
    
    # If no permission config, allow all
    permissions = p_info.get("permissions")
    if not permissions:
        return True
    
    # Check if user's department is in allowed list
    allowed_depts = permissions.get("allowed_depts", [])
    if allowed_depts:
        user_dept = (user_info or {}).get("dept_name", "")
        if user_dept not in allowed_depts:
            return False
    
    # Check if user is in allowed users list
    allowed_users = permissions.get("allowed_users", [])
    if allowed_users:
        userid = (user_info or {}).get("userid", "")
        if userid not in allowed_users:
            return False
    
    return True


@portal_bp.route("/api/get_templates")
def get_templates():
    """获取已配置的模板列表（不拉取审批实例）- 用于首页展示"""
    auth_code = request.args.get("code") or ""
    
    try:
        ding = _ding()
        userid = ding.get_userid_by_auth_code(auth_code)
    except DingTalkError:
        return jsonify({"errcode": 1, "errmsg": "身份校验失败"})
    
    cfg = _cfg()
    user_info = _load_user_info(userid, cfg)
    
    # Load designer layouts (primary source)
    designer_layouts = {}
    try:
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                designer_layouts = data
    except Exception:
        pass
    
    # Load old configs for backward compatibility (fallback)
    old_configs = {}
    try:
        old_configs = load_process_configs(cfg) or {}
    except Exception:
        pass
    
    # Merge: designer layouts take priority
    all_configs = {}
    for p_code, p_info in old_configs.items():
        all_configs[p_code] = p_info
    for p_code, layout in designer_layouts.items():
        all_configs[p_code] = {"name": layout.get("name", p_code), "orientation": layout.get("orientation", "p")}
    
    # Build template list
    templates = []
    for raw_p_code, p_info in all_configs.items():
        p_code = DingTalkService.normalize_code(raw_p_code)
        if not p_code:
            continue
        
        # Check permission
        if not _check_process_permission(user_info, p_code, p_info):
            continue
        
        # Get template name
        if isinstance(p_info, dict):
            template_name = p_info.get("name", p_code)
            orientation = p_info.get("orientation", "p")
        else:
            template_name = p_code
            orientation = "p"
        
        templates.append({
            "p_code": p_code,
            "name": template_name,
            "orientation": orientation,
            "icon": "📄" if orientation == "p" else "📋"
        })
    
    return jsonify({
        "errcode": 0,
        "templates": templates,
        "user_info": {
            "userid": userid,
            "name": (user_info or {}).get("name", ""),
            "dept_name": (user_info or {}).get("dept_name", "")
        }
    })


@portal_bp.route("/api/get_template_instances")
def get_template_instances():
    """获取指定模板的审批实例（支持分页）"""
    auth_code = request.args.get("code") or ""
    p_code = request.args.get("p_code") or ""
    cursor = int(request.args.get("cursor", 0))
    page_size = int(request.args.get("size", 20))
    
    if not p_code:
        return jsonify({"errcode": 1, "errmsg": "缺少模板代码"})
    
    try:
        ding = _ding()
        userid = ding.get_userid_by_auth_code(auth_code)
    except DingTalkError as e:
        current_app.logger.error(f"身份校验失败: {str(e)}")
        return jsonify({"errcode": 1, "errmsg": f"身份校验失败: {str(e)}"})
    
    cfg = _cfg()
    
    # Load template info
    designer_layouts = {}
    try:
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                designer_layouts = data
    except Exception as e:
        current_app.logger.error(f"加载模板配置失败: {str(e)}")
    
    # Try to get template name from designer layouts first
    layout = designer_layouts.get(p_code)
    if layout:
        template_name = layout.get("name", p_code)
    else:
        # Fallback to old configs
        try:
            old_configs = load_process_configs(cfg) or {}
            old_info = old_configs.get(p_code)
            if isinstance(old_info, dict):
                template_name = old_info.get("name", p_code)
            else:
                template_name = p_code
        except Exception:
            template_name = p_code
    
    # Get instances for this template (分页获取)
    my_list = []
    next_cursor = 0
    has_more = False
    
    try:
        current_app.logger.info(f"正在获取审批列表: p_code={p_code}, userid={userid}, cursor={cursor}, size={page_size}")
        
        # 调用钉钉 API 获取一页数据
        token = ding.get_access_token()
        p_code_normalized = ding.normalize_code(p_code)
        start_time_ms = int((time.time() - 120 * 24 * 3600) * 1000)
        
        payload = {
            "process_code": p_code_normalized,
            "start_time": start_time_ms,
            "userid": userid,
            "cursor": cursor,
            "size": page_size,
        }
        
        resp = ding.session.post(
            ding._url("/topapi/processinstance/listids"),
            params={"access_token": token},
            json=payload,
            timeout=ding.cfg.request_timeout_seconds,
        )
        data = resp.json()
        
        if data.get("errcode") != 0:
            raise DingTalkError(f"listids failed: {data}")
        
        result = data.get("result") or {}
        ins_ids = list(result.get("list") or [])
        next_cursor = result.get("next_cursor", 0)
        has_more = next_cursor > 0 and next_cursor != cursor
        
        current_app.logger.info(f"获取到 {len(ins_ids)} 个审批实例 ID, next_cursor={next_cursor}, has_more={has_more}")
        
    except DingTalkError as e:
        error_msg = str(e)
        current_app.logger.error(f"获取审批列表失败: {error_msg}")
        return jsonify({
            "errcode": 1, 
            "errmsg": f"获取审批列表失败: {error_msg}",
            "debug_info": {
                "p_code": p_code,
                "userid": userid,
                "template_name": template_name
            }
        })
    
    # 获取每个审批实例的详细信息（带权限过滤）
    perm = _perm()  # 新增：权限服务
    
    for ins_id in ins_ids:
        try:
            instance = ding.get_process_instance(ins_id)
        except DingTalkError as e:
            current_app.logger.warning(f"获取审批实例失败: ins_id={ins_id}, error={str(e)}")
            continue
        
        # 权限检查：只返回用户有权限查看的审批
        instance_data = {
            "id": ins_id,
            "approval_no": str(instance.get("business_id") or ins_id),
            "title": instance.get("title"),
            "create_time": instance.get("create_time"),
            "status": instance.get("status"),
            "result": instance.get("result"),
            "template_name": template_name,
            "p_code": p_code,
            "originator_userid": instance.get("originator_userid"),  # 用于权限判断
        }
        
        if not perm.can_view_instance(userid, instance_data):
            continue  # 跳过没有权限的审批
        
        my_list.append(instance_data)
    
    current_app.logger.info(f"成功返回 {len(my_list)} 个审批实例")
    
    return jsonify({
        "errcode": 0,
        "list": my_list,
        "template_name": template_name,
        "p_code": p_code,
        "total": len(my_list),
        "cursor": cursor,
        "next_cursor": next_cursor,
        "has_more": has_more
    })



@portal_bp.route("/api/search_template_instances")
def search_template_instances():
    """搜索指定模板的审批实例（后台搜索，不分页，带权限过滤）"""
    auth_code = request.args.get("code") or ""
    p_code = request.args.get("p_code") or ""
    keyword = request.args.get("keyword", "").strip()
    
    if not p_code:
        return jsonify({"errcode": 1, "errmsg": "缺少模板代码"})
    
    try:
        ding = _ding()
        userid = ding.get_userid_by_auth_code(auth_code)
    except DingTalkError as e:
        current_app.logger.error(f"身份校验失败: {str(e)}")
        return jsonify({"errcode": 1, "errmsg": f"身份校验失败: {str(e)}"})
    
    cfg = _cfg()
    perm = _perm()  # 新增：权限服务
    
    # Load template info
    designer_layouts = {}
    try:
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                designer_layouts = data
    except Exception as e:
        current_app.logger.error(f"加载模板配置失败: {str(e)}")
    
    layout = designer_layouts.get(p_code)
    if layout:
        template_name = layout.get("name", p_code)
    else:
        try:
            old_configs = load_process_configs(cfg) or {}
            old_info = old_configs.get(p_code)
            if isinstance(old_info, dict):
                template_name = old_info.get("name", p_code)
            else:
                template_name = p_code
        except Exception:
            template_name = p_code
    
    # 搜索时获取所有数据（最多 200 条）
    my_list = []
    try:
        current_app.logger.info(f"正在搜索审批列表: p_code={p_code}, userid={userid}, keyword={keyword}")
        ins_ids = ding.list_all_process_instance_ids(p_code, userid, max_results=200)
        current_app.logger.info(f"获取到 {len(ins_ids)} 个审批实例")
    except DingTalkError as e:
        error_msg = str(e)
        current_app.logger.error(f"搜索审批列表失败: {error_msg}")
        return jsonify({"errcode": 1, "errmsg": f"搜索失败: {error_msg}"})
    
    # 获取详细信息并筛选（带权限过滤）
    for ins_id in ins_ids:
        try:
            instance = ding.get_process_instance(ins_id)
        except DingTalkError as e:
            current_app.logger.warning(f"获取审批实例失败: ins_id={ins_id}, error={str(e)}")
            continue
        
        title = instance.get("title", "")
        approval_no = str(instance.get("business_id") or ins_id)
        
        # 后台搜索：匹配标题或审批编号
        if keyword:
            if keyword.lower() not in title.lower() and keyword.lower() not in approval_no.lower():
                continue
        
        # 权限检查：只返回用户有权限查看的审批
        instance_data = {
            "id": ins_id,
            "approval_no": approval_no,
            "title": title,
            "create_time": instance.get("create_time"),
            "status": instance.get("status"),
            "result": instance.get("result"),
            "template_name": template_name,
            "p_code": p_code,
            "originator_userid": instance.get("originator_userid"),  # 用于权限判断
        }
        
        if not perm.can_view_instance(userid, instance_data):
            continue  # 跳过没有权限的审批
        
        my_list.append(instance_data)
    
    current_app.logger.info(f"搜索返回 {len(my_list)} 个审批实例")
    
    return jsonify({
        "errcode": 0,
        "list": my_list,
        "template_name": template_name,
        "p_code": p_code,
        "total": len(my_list),
        "keyword": keyword
    })


@portal_bp.route("/api/get_my_list")
def get_my_list():
    auth_code = request.args.get("code") or ""

    try:
        ding = _ding()
        userid = ding.get_userid_by_auth_code(auth_code)
    except DingTalkError:
        return jsonify({"errcode": 1, "errmsg": "身份校验失败"})

    cfg = _cfg()
    
    # Load user info for permission check
    user_info = _load_user_info(userid, cfg)
    
    # Load designer layouts (primary source)
    designer_layouts = {}
    try:
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                designer_layouts = data
    except Exception:
        pass
    
    # Load old configs for backward compatibility (fallback)
    old_configs = {}
    try:
        old_configs = load_process_configs(cfg) or {}
    except Exception:
        pass
    
    # Merge: designer layouts take priority
    all_configs = {}
    
    # First, add old configs
    for p_code, p_info in old_configs.items():
        all_configs[p_code] = p_info
    
    # Then, override with designer layouts (priority)
    for p_code, layout in designer_layouts.items():
        all_configs[p_code] = {"name": layout.get("name", p_code)}

    # Collect available process templates for filter
    available_templates = {}
    my_list = []
    
    for raw_p_code, p_info in (all_configs or {}).items():
        p_code = DingTalkService.normalize_code(raw_p_code)
        if not p_code:
            continue
        
        # Check permission
        if not _check_process_permission(user_info, p_code, p_info):
            continue
        
        # Get template name, handle both old and new format
        if isinstance(p_info, dict):
            template_name = p_info.get("name", p_code)
        else:
            template_name = p_code
        
        available_templates[p_code] = template_name
        
        try:
            ins_ids = ding.list_process_instance_ids(p_code, userid)
        except DingTalkError:
            continue

        for ins_id in ins_ids:
            try:
                instance = ding.get_process_instance(ins_id)
            except DingTalkError:
                continue
            my_list.append(
                {
                    "id": ins_id,
                    # Use DingTalk detail header approval number (business_id) when available.
                    "approval_no": str(instance.get("business_id") or ins_id),
                    "title": instance.get("title"),
                    "create_time": instance.get("create_time"),
                    # For portal UI status badges (best-effort; DingTalk fields vary)
                    "status": instance.get("status"),
                    "result": instance.get("result"),
                    "template_name": template_name,
                    "p_code": p_code,
                }
            )

    return jsonify({
        "errcode": 0, 
        "list": my_list,
        "templates": available_templates,
        "user_info": {
            "userid": userid,
            "name": (user_info or {}).get("name", ""),
            "dept_name": (user_info or {}).get("dept_name", "")
        }
    })

