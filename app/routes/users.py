from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request

from app.services.dingtalk_service import DingTalkError, DingTalkService


users_bp = Blueprint("users_bp", __name__)


def _cfg():
    return current_app.extensions["app_cfg"]


def _ding() -> DingTalkService:
    return current_app.extensions["dingtalk"]


def _users_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "users.json"


def _signature_bindings_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "process_signature_bindings.json"


def _print_layouts_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "print_layouts.json"


def _node_names_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "process_node_names.json"


def _load_users_data() -> dict:
    """Load local users data"""
    path = _users_path()
    if not path.exists():
        return {"users": [], "departments": [], "signature_slots": {}, "last_sync": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {"users": [], "departments": [], "signature_slots": {}, "last_sync": None}
    except Exception:
        return {"users": [], "departments": [], "signature_slots": {}, "last_sync": None}


def _save_users_data(data: dict) -> None:
    """Save local users data"""
    path = _users_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_signature_bindings() -> dict:
    path = _signature_bindings_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_signature_bindings(data: dict) -> None:
    path = _signature_bindings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_print_layouts() -> dict:
    path = _print_layouts_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _load_node_name_map() -> dict:
    path = _node_names_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_node_name_map(data: dict) -> None:
    path = _node_names_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data or {}, ensure_ascii=False, indent=2), encoding="utf-8")


@users_bp.route("/admin/users")
def users_list():
    """User management page"""
    return render_template("users_list.html")


@users_bp.route("/admin/signature-bindings")
def signature_bindings_page():
    """Process signature field to local user binding page."""
    return render_template("signature_bindings.html")


@users_bp.route("/api/signature_bindings/processes")
def signature_binding_processes():
    layouts = _load_print_layouts()
    rows = []
    for code, layout in layouts.items():
        if not isinstance(layout, dict):
            continue
        rows.append({
            "process_code": code,
            "name": layout.get("name") or code,
        })
    rows.sort(key=lambda x: (str(x.get("name") or ""), str(x.get("process_code") or "")))
    return jsonify({"ok": True, "processes": rows})


@users_bp.route("/api/signature_bindings/users")
def signature_binding_users():
    data = _load_users_data()
    users = data.get("users", []) if isinstance(data, dict) else []
    if not isinstance(users, list):
        users = []
    rows = []
    for u in users:
        if not isinstance(u, dict):
            continue
        rows.append({
            "userid": str(u.get("userid") or ""),
            "name": str(u.get("name") or ""),
            "dept_name": str(u.get("dept_name") or ""),
            "dept_path_name": str(u.get("dept_path_name") or ""),
            "is_active": bool(u.get("is_active", True)),
        })
    rows.sort(key=lambda x: (0 if x.get("is_active") else 1, x.get("name") or "", x.get("dept_name") or ""))
    return jsonify({"ok": True, "users": rows})


@users_bp.route("/api/signature_bindings/get")
def signature_binding_get():
    process_code = str(request.args.get("process_code") or "").strip()
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code"}), 400
    all_bindings = _load_signature_bindings()
    row = all_bindings.get(process_code, {}) if isinstance(all_bindings, dict) else {}
    return jsonify({"ok": True, "process_code": process_code, "item": row if isinstance(row, dict) else {}})


@users_bp.route("/api/signature_bindings/fields", methods=["GET", "POST"])
def signature_binding_fields():
    payload = request.get_json(silent=True) or {}
    process_code = str(request.args.get("process_code") or payload.get("process_code") or "").strip()
    instance_id = str(request.args.get("instance_id") or payload.get("instance_id") or "").strip()
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code"}), 400
    ding = _ding()
    try:
        if not instance_id:
            userid = str(os.getenv("DINGTALK_ADMIN_USERID") or "").strip()
            if not userid:
                return jsonify({"ok": False, "msg": "缺少 instance_id，且未配置 DINGTALK_ADMIN_USERID"}), 400
            ids = ding.list_process_instance_ids(process_code, userid, size=1)
            if not ids:
                return jsonify({"ok": False, "msg": "未找到可用于读取控件的流程实例"}), 404
            instance_id = ids[0]
        instance = ding.get_process_instance(instance_id)
    except DingTalkError as e:
        return jsonify({"ok": False, "msg": str(e)}), 400
    fields = []
    source_fields = []
    for comp in (instance or {}).get("form_component_values", []) or []:
        if not isinstance(comp, dict):
            continue
        ctype = str(comp.get("component_type") or "").strip()
        comp_id = str(comp.get("id") or "")
        comp_name = str(comp.get("name") or "")
        row = {
            "field_id": comp_id,
            "field_name": comp_name,
            "field_type": ctype,
            "value_preview": str(comp.get("value") or "")[:120],
            "has_value": bool(str(comp.get("value") or "").strip()),
        }
        if ctype == "SignatureField":
            fields.append(row)
        else:
            source_fields.append(row)
    nodes = []
    node_name_map_all = _load_node_name_map()
    process_node_map = node_name_map_all.get(process_code, {}) if isinstance(node_name_map_all, dict) else {}
    if not isinstance(process_node_map, dict):
        process_node_map = {}
    for task in (instance or {}).get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        activity_id = str(task.get("activity_id") or "")
        api_activity_name = str(task.get("activity_name") or "")
        display_activity_name = str(process_node_map.get(activity_id) or api_activity_name or "").strip()
        nodes.append({
            "activity_id": activity_id,
            "activity_name": display_activity_name,
            "api_activity_name": api_activity_name,
            "userid": str(task.get("userid") or ""),
            "task_status": str(task.get("task_status") or ""),
            "task_result": str(task.get("task_result") or ""),
            "finish_time": str(task.get("finish_time") or ""),
        })
    return jsonify({"ok": True, "process_code": process_code, "instance_id": instance_id, "fields": fields, "source_fields": source_fields, "nodes": nodes})


@users_bp.route("/api/signature_bindings/node_names", methods=["GET", "POST"])
def signature_binding_node_names():
    process_code = str((request.values.get("process_code") if request.method == "POST" else request.args.get("process_code")) or "").strip()
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code"}), 400
    all_map = _load_node_name_map()
    if not isinstance(all_map, dict):
        all_map = {}
    if request.method == "GET":
        curr = all_map.get(process_code, {})
        return jsonify({"ok": True, "process_code": process_code, "node_names": curr if isinstance(curr, dict) else {}})
    payload = request.get_json(silent=True) or {}
    node_names = payload.get("node_names")
    if not isinstance(node_names, dict):
        return jsonify({"ok": False, "msg": "node_names 必须是对象"}), 400
    clean = {}
    for k, v in node_names.items():
        key = str(k or "").strip()
        val = str(v or "").strip()
        if key and val:
            clean[key] = val
    all_map[process_code] = clean
    _save_node_name_map(all_map)
    return jsonify({"ok": True, "msg": "节点标题保存成功", "node_names": clean})


@users_bp.route("/api/signature_bindings/save", methods=["POST"])
def signature_binding_save():
    payload = request.get_json(silent=True) or {}
    process_code = str(payload.get("process_code") or "").strip()
    process_name = str(payload.get("process_name") or "").strip()
    bindings = payload.get("bindings") or {}
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code"}), 400
    if not isinstance(bindings, dict):
        return jsonify({"ok": False, "msg": "bindings 必须是对象"}), 400
    users_data = _load_users_data()
    users = users_data.get("users", []) if isinstance(users_data, dict) else []
    users_by_id = {str(u.get("userid") or ""): u for u in users if isinstance(u, dict)}
    clean = {}
    for field_id, row in bindings.items():
        fid = str(field_id or "").strip()
        if not fid or not isinstance(row, dict):
            continue
        uid = str(row.get("local_userid") or "").strip()
        user = users_by_id.get(uid, {}) if uid else {}
        clean[fid] = {
            "field_id": fid,
            "field_name": str(row.get("field_name") or "").strip(),
            "field_type": "SignatureField",
            "source_type": str(row.get("source_type") or "form_field").strip() or "form_field",
            "source_field_id": str(row.get("source_field_id") or "").strip(),
            "source_field_name": str(row.get("source_field_name") or "").strip(),
            "source_field_type": str(row.get("source_field_type") or "").strip(),
            "activity_id": str(row.get("activity_id") or "").strip(),
            "activity_name": str(row.get("activity_name") or "").strip(),
            "local_userid": uid,
            "local_user_name": str((user or {}).get("name") or row.get("local_user_name") or "").strip(),
            "dept_name": str((user or {}).get("dept_name") or row.get("dept_name") or "").strip(),
            "dept_path_name": str((user or {}).get("dept_path_name") or row.get("dept_path_name") or "").strip(),
        }
    all_bindings = _load_signature_bindings()
    all_bindings[process_code] = {
        "process_code": process_code,
        "process_name": process_name or process_code,
        "bindings": clean,
        "updated_at": datetime.now().isoformat(),
    }
    _save_signature_bindings(all_bindings)
    return jsonify({"ok": True, "msg": "保存成功", "count": len(clean)})


@users_bp.route("/api/users/sync", methods=["POST"])
def sync_users():
    """Sync users from DingTalk (recursive all departments)"""
    try:
        ding = _ding()
        include_mobile = str(request.args.get("include_mobile") or "0").strip() == "1"
        
        # Recursively get all departments
        def get_all_departments(parent_id=None, parent_path=None, level=0):
            """Recursively get all departments with hierarchy path"""
            depts = []
            parent_path = parent_path or []
            try:
                dept_list = ding.get_department_list(parent_id)
                for dept in dept_list:
                    dept_id = str(dept.get("dept_id", ""))
                    original_name = str(dept.get("name", ""))
                    path_names = parent_path + [original_name]
                    dept_info = {
                        "dept_id": dept_id,
                        "name": original_name,
                        "original_name": original_name,
                        "parent_id": str(dept.get("parent_id", "")) if dept.get("parent_id") else None,
                        "order": dept.get("order", 0),
                        "level": level,
                        "path_name": " / ".join(path_names),
                    }
                    depts.append(dept_info)
                    sub_depts = get_all_departments(dept_id, path_names, level + 1)
                    depts.extend(sub_depts)
            except DingTalkError:
                pass
            return depts
        
        # Get all departments starting from root
        departments = get_all_departments()
        
        # Get all users from all departments
        all_users = []
        user_ids_seen = set()
        mobile_denied_count = 0
        
        for dept in departments:
            try:
                users_in_dept = ding.get_dept_user_list(dept["dept_id"])
                for user in users_in_dept:
                    userid = str(user.get("userid", ""))
                    if userid and userid not in user_ids_seen:
                        user_ids_seen.add(userid)
                        detail = {}
                        if include_mobile:
                            try:
                                detail = ding.get_user_detail(userid)
                            except DingTalkError:
                                mobile_denied_count += 1
                        mobile = str(detail.get("mobile") or user.get("mobile") or "")
                        all_users.append({
                            "userid": userid,
                            "name": detail.get("name") or user.get("name", ""),
                            "dept_id": dept["dept_id"],
                            "dept_name": dept["name"],
                            "dept_path_name": dept.get("path_name") or dept["name"],
                            "dept_level": dept.get("level", 0),
                            "mobile": mobile,
                            "signature_slot": None,
                            "is_active": True,
                            "synced_at": datetime.now().isoformat(),
                        })
            except DingTalkError:
                continue
        
        # Load existing data to preserve manual edits
        existing_data = _load_users_data()
        existing_users = {u["userid"]: u for u in existing_data.get("users", [])}
        existing_depts = {d["dept_id"]: d for d in existing_data.get("departments", [])}
        
        # Merge: preserve manual edits (dept_name, signature_slot)
        merged_users = []
        for user in all_users:
            if user["userid"] in existing_users:
                old_user = existing_users[user["userid"]]
                # Preserve manual edits
                user["dept_name"] = old_user.get("dept_name", user["dept_name"])
                user["dept_path_name"] = old_user.get("dept_path_name", user.get("dept_path_name", user["dept_name"]))
                user["signature_slot"] = old_user.get("signature_slot")
                user["is_active"] = old_user.get("is_active", True)
                if old_user.get("mobile") and not user.get("mobile"):
                    user["mobile"] = old_user.get("mobile")
            merged_users.append(user)
        
        # Mark users not in sync as potentially inactive (but don't auto-change)
        for userid, old_user in existing_users.items():
            if userid not in user_ids_seen:
                # Keep old user but mark synced_at as old
                merged_users.append(old_user)
        
        # Merge departments
        merged_depts = []
        for dept in departments:
            if dept["dept_id"] in existing_depts:
                old_dept = existing_depts[dept["dept_id"]]
                # Preserve manual name edits
                dept["name"] = old_dept.get("name", dept["name"])
            merged_depts.append(dept)
        
        # Save
        data = {
            "users": merged_users,
            "departments": merged_depts,
            "signature_slots": existing_data.get("signature_slots", {}),
            "last_sync": datetime.now().isoformat(),
        }
        _save_users_data(data)
        
        mobile_msg = f"手机号详情失败/无权限：{mobile_denied_count} 个" if include_mobile else "未同步手机号（如需手机号，需开通通讯录敏感字段权限后使用手机号同步）"
        return jsonify({
            "ok": True,
            "msg": f"同步成功：{len(merged_users)} 个用户，{len(merged_depts)} 个部门（含子部门）。{mobile_msg}",
            "users_count": len(merged_users),
            "depts_count": len(merged_depts),
            "mobile_denied_count": mobile_denied_count,
        })
    
    except DingTalkError as e:
        return jsonify({"ok": False, "msg": f"钉钉 API 错误: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"ok": False, "msg": f"同步失败: {str(e)}"}), 500


@users_bp.route("/api/users/list")
def get_users_list():
    """Get local users list"""
    data = _load_users_data()
    return jsonify({
        "ok": True,
        "users": data.get("users", []),
        "departments": data.get("departments", []),
        "last_sync": data.get("last_sync"),
    })


@users_bp.route("/api/users/sync_mobile", methods=["POST"])
def sync_mobile_numbers():
    """Sync mobile numbers for existing local users only."""
    try:
        ding = _ding()
        data = _load_users_data()
        users = data.get("users", [])
        updated = 0
        failed = 0
        unchanged = 0
        for user in users:
            userid = str(user.get("userid") or "").strip()
            if not userid:
                failed += 1
                continue
            try:
                detail = ding.get_user_detail(userid)
                mobile = str(detail.get("mobile") or "")
                if mobile:
                    if user.get("mobile") != mobile:
                        user["mobile"] = mobile
                        updated += 1
                    else:
                        unchanged += 1
                else:
                    failed += 1
            except DingTalkError:
                failed += 1
        data["users"] = users
        data["last_mobile_sync"] = datetime.now().isoformat()
        _save_users_data(data)
        return jsonify({
            "ok": True,
            "msg": f"手机号同步完成：更新 {updated} 个，未变化 {unchanged} 个，失败/无权限 {failed} 个",
            "updated": updated,
            "unchanged": unchanged,
            "failed": failed,
        })
    except Exception as e:
        return jsonify({"ok": False, "msg": f"手机号同步失败: {str(e)}"}), 500


@users_bp.route("/api/users/update", methods=["POST"])
def update_user():
    """Update user info (dept_name, signature_slot, is_active)"""
    try:
        payload = request.get_json() or {}
        userid = str(payload.get("userid", "")).strip()
        if not userid:
            return jsonify({"ok": False, "msg": "缺少 userid"}), 400
        
        data = _load_users_data()
        users = data.get("users", [])
        
        # Find and update user
        user_found = False
        for user in users:
            if user["userid"] == userid:
                user_found = True
                if "dept_name" in payload:
                    user["dept_name"] = str(payload["dept_name"]).strip()
                if "signature_slot" in payload:
                    slot = payload["signature_slot"]
                    user["signature_slot"] = int(slot) if slot else None
                if "is_active" in payload:
                    user["is_active"] = bool(payload["is_active"])
                break
        
        if not user_found:
            return jsonify({"ok": False, "msg": "用户不存在"}), 404
        
        data["users"] = users
        _save_users_data(data)
        
        return jsonify({"ok": True, "msg": "更新成功"})
    
    except Exception as e:
        return jsonify({"ok": False, "msg": f"更新失败: {str(e)}"}), 500


@users_bp.route("/api/departments/update", methods=["POST"])
def update_department():
    """Update department name"""
    try:
        payload = request.get_json() or {}
        dept_id = str(payload.get("dept_id", "")).strip()
        new_name = str(payload.get("name", "")).strip()
        
        if not dept_id or not new_name:
            return jsonify({"ok": False, "msg": "缺少 dept_id 或 name"}), 400
        
        data = _load_users_data()
        departments = data.get("departments", [])
        
        # Update department
        dept_found = False
        for dept in departments:
            if dept["dept_id"] == dept_id:
                dept_found = True
                dept["name"] = new_name
                break
        
        if not dept_found:
            return jsonify({"ok": False, "msg": "部门不存在"}), 404
        
        # Update all users in this department
        users = data.get("users", [])
        for user in users:
            if user["dept_id"] == dept_id:
                user["dept_name"] = new_name
        
        data["departments"] = departments
        data["users"] = users
        _save_users_data(data)
        
        return jsonify({"ok": True, "msg": "更新成功"})
    
    except Exception as e:
        return jsonify({"ok": False, "msg": f"更新失败: {str(e)}"}), 500
