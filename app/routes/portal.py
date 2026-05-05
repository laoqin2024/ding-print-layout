from __future__ import annotations

import json

from flask import Blueprint, current_app, jsonify, render_template, request

from app.services.dingtalk_service import DingTalkError, DingTalkService
from app.services.pdf_service import load_process_configs


portal_bp = Blueprint("portal_bp", __name__)


def _cfg():
    return current_app.extensions["app_cfg"]


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
    # If no permission config, allow all
    permissions = (p_info or {}).get("permissions")
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
    
    # Load both old configs and new designer layouts
    configs = load_process_configs(cfg)
    
    # Load designer layouts
    designer_layouts = {}
    try:
        layouts_path = cfg.base_dir / "data" / "print_layouts.json"
        if layouts_path.exists():
            data = json.loads(layouts_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                designer_layouts = data
    except Exception:
        pass
    
    # Merge: designer layouts take priority
    all_configs = {}
    for p_code, p_info in (configs or {}).items():
        all_configs[p_code] = p_info
    
    for p_code, layout in designer_layouts.items():
        if p_code not in all_configs:
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
        
        template_name = (p_info or {}).get("name", p_code)
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

