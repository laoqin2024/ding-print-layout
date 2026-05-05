from __future__ import annotations

import json
import os
import re
import base64
from datetime import datetime
from pathlib import Path

from flask import Blueprint, current_app, jsonify, redirect, render_template, request, send_file, url_for, has_request_context

from app.services.dingtalk_service import DingTalkError, DingTalkService
from app.services.pdf_service import list_pdf_templates, render_pdf_page_png


designer_bp = Blueprint("designer_bp", __name__)


def _cfg():
    return current_app.extensions["app_cfg"]


def _ding() -> DingTalkService:
    return current_app.extensions["dingtalk"]


def _layouts_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "print_layouts.json"


def _load_layouts() -> dict:
    path = _layouts_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_layouts(data: dict) -> None:
    path = _layouts_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data or {}, ensure_ascii=False, indent=2), encoding="utf-8")


def _node_name_map_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "designer_node_names.json"


def _load_node_name_map() -> dict:
    path = _node_name_map_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_node_name_map(data: dict) -> None:
    path = _node_name_map_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data or {}, ensure_ascii=False, indent=2), encoding="utf-8")


def _stamp_assets_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "designer_stamp_assets.json"


def _load_stamp_assets() -> dict:
    path = _stamp_assets_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_stamp_assets(data: dict) -> None:
    path = _stamp_assets_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data or {}, ensure_ascii=False, indent=2), encoding="utf-8")


def _instance_qr_map_path() -> Path:
    cfg = _cfg()
    return cfg.base_dir / "data" / "instance_qr_links.json"


def _load_instance_qr_map() -> dict:
    path = _instance_qr_map_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_instance_qr_map(data: dict) -> None:
    path = _instance_qr_map_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data or {}, ensure_ascii=False, indent=2), encoding="utf-8")


def _trusted_qr_map_row(qr_row: dict, *, process_code: str, instance: dict) -> bool:
    """回填的 aflow/qr 必须与当前请求的 process_code 及实例 business_id 一致，否则视为串数据。"""
    if not isinstance(qr_row, dict):
        return False
    row_pc = DingTalkService.normalize_code(str(qr_row.get("process_code") or ""))
    if not row_pc:
        return False
    if row_pc != DingTalkService.normalize_code(process_code or ""):
        return False
    row_bid = str(qr_row.get("business_id") or "").strip()
    inst_bid = str((instance or {}).get("business_id") or "").strip()
    if inst_bid:
        if not row_bid or row_bid != inst_bid:
            return False
    return True


def _text_len(fitz_mod, s: str, fontname: str, fontsize: float) -> float:
    try:
        length = float(fitz_mod.get_text_length(s, fontname=fontname, fontsize=fontsize))
        # 调试：如果是自定义字体，打印宽度信息
        if fontname == "F0":
            print(f"[DEBUG] _text_len: text='{s}', fontname={fontname}, fontsize={fontsize}, length={length}")
        return length
    except Exception as e:
        # fallback rough estimate
        fallback = max(0.0, len(s) * fontsize * 0.55)
        print(f"[DEBUG] _text_len fallback: text='{s}', fontname={fontname}, error={e}, fallback={fallback}")
        return fallback


def _contains_cjk(s: str) -> bool:
    return bool(re.search(r"[\u3400-\u9fff\uf900-\ufaff]", str(s or "")))


def _pick_designer_cjk_fontfile() -> str | None:
    # Keep designer preview lightweight: use system CJK fonts only when needed.
    candidates = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    return None


def _page_visual_orient(page) -> str:
    rot = int(getattr(page, "rotation", 0) or 0) % 360
    w = float(page.rect.width)
    h = float(page.rect.height)
    vw, vh = (h, w) if rot in (90, 270) else (w, h)
    return "l" if vw >= vh else "p"


def _build_system_fields(instance: dict, process_code: str, instance_id: str) -> list[dict]:
    inst = instance or {}
    tasks = inst.get("tasks") or []
    first_task = tasks[0] if isinstance(tasks, list) and tasks and isinstance(tasks[0], dict) else {}
    activity_id = str(first_task.get("activity_id") or "")
    task_url_raw = str(first_task.get("url") or "").strip()

    def _normalize_dingtalk_url(raw: str) -> str:
        s = str(raw or "").strip()
        if not s:
            return ""
        if s.startswith("http://") or s.startswith("https://"):
            return s
        # common DingTalk task URL from APIs: aflow.dingtalk.com?procInsId=...
        if s.startswith("aflow.dingtalk.com?"):
            return "https://aflow.dingtalk.com/?" + s.split("?", 1)[1]
        if s.startswith("aflow.dingtalk.com/"):
            return "https://" + s
        return "https://" + s

    def _is_aflow_qr_url(raw: str) -> bool:
        s = str(raw or "").strip().lower()
        return s.startswith("https://aflow.dingtalk.com/qr/") or s.startswith("aflow.dingtalk.com/qr/")

    def _extract_aflow_qr_url(raw: str) -> str:
        s = str(raw or "").strip()
        if not s:
            return ""
        s_norm = _normalize_dingtalk_url(s)
        if _is_aflow_qr_url(s_norm):
            return s_norm
        try:
            m = re.search(r"(https?://aflow\.dingtalk\.com/qr/[A-Za-z0-9_-]+)", s, flags=re.I)
            if m:
                return m.group(1)
            m2 = re.search(r"(aflow\.dingtalk\.com/qr/[A-Za-z0-9_-]+)", s, flags=re.I)
            if m2:
                return "https://" + m2.group(1)
        except Exception:
            return ""
        return ""

    task_url = _normalize_dingtalk_url(task_url_raw)
    scan_entry_url = ""
    if instance_id:
        if has_request_context():
            try:
                scan_entry_url = url_for("print_bp.open_approval", id=instance_id, _external=True)
            except Exception:
                scan_entry_url = ""
        if not scan_entry_url:
            base = str(os.getenv("PUBLIC_BASE_URL") or "").strip().rstrip("/")
            if base:
                scan_entry_url = f"{base}/open_approval?id={instance_id}"
    # Only expose verified DingTalk aflow /qr/ links; do not fabricate by instance id.
    aflow_qr_entry = ""
    qr_map = _load_instance_qr_map()
    qr_row = qr_map.get(instance_id, {}) if isinstance(qr_map, dict) else {}
    if not isinstance(qr_row, dict):
        qr_row = {}
    raw_map_qr = _normalize_dingtalk_url(str(qr_row.get("qr_url") or "").strip())
    # 旧版回填未写 process_code，无法证明短链属于本流程，直接移除以免串单。
    if (
        instance_id
        and raw_map_qr
        and _is_aflow_qr_url(raw_map_qr)
        and not str(qr_row.get("process_code") or "").strip()
    ):
        try:
            if isinstance(qr_map, dict) and instance_id in qr_map:
                del qr_map[instance_id]
                _save_instance_qr_map(qr_map)
            qr_row = {}
            raw_map_qr = ""
        except Exception:
            qr_row = {}
            raw_map_qr = ""

    map_trusted = bool(
        raw_map_qr
        and _is_aflow_qr_url(raw_map_qr)
        and _trusted_qr_map_row(qr_row, process_code=process_code, instance=inst)
    )
    instance_qr_url = raw_map_qr if map_trusted else ""

    task_qr_url = _extract_aflow_qr_url(task_url_raw) or _extract_aflow_qr_url(task_url)
    # Preferred QR link policy (strict):
    # - only aflow /qr/ short link is accepted
    # - do not fallback to long task URLs
    if map_trusted and _is_aflow_qr_url(instance_qr_url):
        preferred_qr_url = instance_qr_url
    elif _is_aflow_qr_url(task_qr_url):
        preferred_qr_url = task_qr_url
    else:
        preferred_qr_url = ""
    aflow_qr_entry = preferred_qr_url
    if preferred_qr_url:
        preferred_qr_status = "已绑定专属二维码"
    else:
        if raw_map_qr and _is_aflow_qr_url(raw_map_qr) and not map_trusted:
            row_pc = str(qr_row.get("process_code") or "").strip()
            if not row_pc:
                preferred_qr_status = "旧回填缺少流程校验已忽略，请重新绑定当前实例的 aflow/qr"
            else:
                preferred_qr_status = "回填与当前流程或审批编号不一致，已忽略"
        else:
            preferred_qr_status = "未获取到专属二维码（aflow/qr）"

    # Auto-backfill verified aflow /qr/ links into map for reuse.
    try:
        if instance_id and _is_aflow_qr_url(task_qr_url):
            qr_map2 = _load_instance_qr_map()
            if not isinstance(qr_map2, dict):
                qr_map2 = {}
            prev_row = qr_map2.get(instance_id, {})
            if not isinstance(prev_row, dict):
                prev_row = {}
            prev = str(prev_row.get("qr_url") or "").strip()
            if prev != task_qr_url:
                qr_map2[instance_id] = {
                    **prev_row,
                    "qr_url": task_qr_url,
                    "process_code": DingTalkService.normalize_code(process_code or ""),
                    "business_id": str(inst.get("business_id") or "").strip(),
                    "source": "auto_task_url",
                    "updated_at": datetime.utcnow().isoformat(),
                }
                _save_instance_qr_map(qr_map2)
    except Exception:
        pass
    node_name_map_all = _load_node_name_map()
    process_node_map = node_name_map_all.get(process_code, {}) if isinstance(node_name_map_all, dict) else {}
    if not isinstance(process_node_map, dict):
        process_node_map = {}

    entries = [
        ("sys.instance_id", "实例ID", "SystemField", instance_id),
        ("sys.process_code", "流程Code", "SystemField", process_code),
        ("sys.approval_no", "审批编号", "SystemField", inst.get("business_id")),
        ("sys.title", "审批标题", "SystemField", inst.get("title")),
        ("sys.originator_userid", "发起人UserId", "SystemField", inst.get("originator_userid")),
        ("sys.originator_dept_id", "发起部门ID", "SystemField", inst.get("originator_dept_id")),
        ("sys.create_time", "发起时间", "SystemField", inst.get("create_time")),
        ("sys.finish_time", "流程完成时间", "SystemField", inst.get("finish_time")),
        ("sys.result", "流程结果", "SystemField", inst.get("result")),
        ("sys.status", "流程状态", "SystemField", inst.get("status")),
        ("sys.current_activity_id", "当前节点ID", "SystemField", activity_id),
        ("sys.current_activity_name", "当前节点中文名", "SystemField", process_node_map.get(activity_id)),
        ("sys.current_task_url", "当前任务链接（钉钉直链）", "SystemField", task_url),
        ("sys.preferred_qr_url", "二维码优先链接（推荐）", "SystemField", preferred_qr_url),
        ("sys.preferred_qr_status", "二维码绑定状态", "SystemField", preferred_qr_status),
        ("sys.scan_entry_url", "扫码稳定入口", "SystemField", scan_entry_url),
        ("sys.aflow_qr_entry", "钉钉扫码入口", "SystemField", aflow_qr_entry),
        ("sys.instance_qr_url", "实例二维码链接（回填）", "SystemField", instance_qr_url),
    ]
    out = []
    for fid, name, ctype, raw in entries:
        sval = "" if raw is None else str(raw)
        out.append(
            {
                "id": fid,
                "name": name,
                "type": ctype,
                "value": sval,
                "value_preview": sval[:180] + "..." if len(sval) > 180 else sval,
            }
        )
    return out


def _instance_process_code(instance: dict) -> str:
    if not isinstance(instance, dict):
        return ""
    raw = instance.get("process_code")
    if raw is None:
        raw = instance.get("processCode")
    return DingTalkService.normalize_code(raw or "")


def _flow_result_text_and_color(instance: dict) -> tuple[str, tuple[float, float, float]]:
    """
    Auto flow-result text + color:
    - 审批通过: RGB(27,176,87)
    - 审批拒绝: red-ish
    - 已撤销: gray-ish
    - 等待{当前审批人}处理: RGB(255,147,60)
    """
    inst = instance or {}
    raw = str(inst.get("result") or inst.get("status") or "").strip().lower()
    if raw in ("agree", "approved", "pass", "passed", "completed"):
        return "审批通过", (27 / 255.0, 176 / 255.0, 87 / 255.0)
    if raw in ("refuse", "reject", "rejected"):
        return "审批拒绝", (225 / 255.0, 29 / 255.0, 72 / 255.0)
    if raw in ("revoke", "revoked", "cancel", "canceled", "cancelled"):
        return "已撤销", (100 / 255.0, 116 / 255.0, 139 / 255.0)

    # Waiting: try to infer current approver(s) from unfinished tasks.
    tasks = inst.get("tasks") or []
    approvers: list[str] = []
    for t in tasks if isinstance(tasks, list) else []:
        if not isinstance(t, dict):
            continue
        finish = str(t.get("finish_time") or t.get("finishTime") or "").strip()
        tstatus = str(t.get("task_status") or t.get("status") or "").strip().lower()
        tresult = str(t.get("task_result") or t.get("result") or "").strip().lower()
        if finish:
            continue
        if tstatus in ("completed", "finished", "done"):
            continue
        if tresult in ("agree", "approved", "pass", "passed", "refuse", "reject", "rejected", "revoke", "revoked"):
            continue
        name = str(
            t.get("user_name")
            or t.get("userName")
            or t.get("username")
            or t.get("nick")
            or t.get("userid")
            or ""
        ).strip()
        if name and name not in approvers:
            approvers.append(name)

    if not approvers:
        pending = "当前审批人"
    elif len(approvers) == 1:
        pending = approvers[0]
    elif len(approvers) == 2:
        pending = f"{approvers[0]}、{approvers[1]}"
    else:
        pending = f"{approvers[0]}等{len(approvers)}人"
    return f"等待{pending}处理", (255 / 255.0, 147 / 255.0, 60 / 255.0)


def _extract_signature_items_from_component_value(raw) -> list[dict]:
    """
    Extract signature items from DingTalk component value.
    Returns list of {url, userid, name, data_id} dicts.
    """
    items: list[dict] = []
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("http://") or s.startswith("https://"):
            return [{"url": s, "userid": "", "name": "", "data_id": ""}]
        if s.startswith("[") or s.startswith("{"):
            try:
                raw = json.loads(s)
            except Exception:
                return []
        else:
            return []
    if isinstance(raw, dict):
        url = ""
        for k in ("url", "mediaId", "media_id", "downloadUrl", "download_url", "signatureUrl", "signUrl"):
            v = str(raw.get(k) or "").strip()
            if v.startswith("http://") or v.startswith("https://"):
                url = v
                break
        userid = ""
        for k in ("userid", "userId", "user_id", "staffId", "staff_id", "dingUserId", "ding_user_id", "employeeId", "employee_id"):
            v = str(raw.get(k) or "").strip()
            if v:
                userid = v
                break
        name = ""
        for k in ("name", "userName", "user_name", "signerName", "signer_name", "operatorName", "operator_name", "nick"):
            v = str(raw.get(k) or "").strip()
            if v:
                name = v
                break
        data_id = ""
        for k in ("id", "dataId", "data_id", "valueId", "value_id", "bizId", "biz_id"):
            v = str(raw.get(k) or "").strip()
            if v:
                data_id = v
                break
        if url:
            items.append({"url": url, "userid": userid, "name": name, "data_id": data_id})
        for k in ("list", "items", "value", "values", "data", "signatures"):
            nested = raw.get(k)
            if isinstance(nested, (list, dict, str)):
                items.extend(_extract_signature_items_from_component_value(nested))
        return items
    if isinstance(raw, list):
        for item in raw:
            items.extend(_extract_signature_items_from_component_value(item))
    return [it for it in items if it.get("url")]


def _collect_form_signature_map(instance: dict) -> dict[str, str]:
    """
    Build userid -> signature_url mapping from form signature components.
    Returns dict: {userid: url}
    
    NOTE: DingTalk signature component value is often just a plain URL string,
    without userid metadata. This function is kept for potential future use
    but may return empty dict in most cases.
    """
    sig_items: list[dict] = []
    for comp in (instance or {}).get("form_component_values", []) or []:
        if not isinstance(comp, dict):
            continue
        ctype = str(comp.get("component_type") or "").strip()
        if ctype not in ("SignatureField", "DDSingleSign", "DDSign", "DDAttachmentSign"):
            continue
        sig_items.extend(_extract_signature_items_from_component_value(comp.get("value")))
    
    # Build userid -> url map (last wins if duplicate)
    userid_map: dict[str, str] = {}
    for it in sig_items:
        uid = str(it.get("userid") or "").strip()
        url = str(it.get("url") or "").strip()
        if uid and url:
            userid_map[uid] = url
    return userid_map


def _load_local_users_indexes() -> tuple[dict[str, dict], dict[str, list[dict]]]:
    cfg = _cfg()
    path = cfg.base_dir / "data" / "users.json"
    if not path.exists():
        return {}, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}, {}
    users = data.get("users") if isinstance(data, dict) else []
    if not isinstance(users, list):
        return {}, {}
    by_userid: dict[str, dict] = {}
    by_name: dict[str, list[dict]] = {}
    for user in users:
        if not isinstance(user, dict):
            continue
        uid = str(user.get("userid") or "").strip()
        name = str(user.get("name") or "").strip()
        if uid:
            by_userid[uid] = user
        if name:
            by_name.setdefault(name, []).append(user)
    return by_userid, by_name


def _load_local_users_index() -> dict[str, dict]:
    by_userid, _ = _load_local_users_indexes()
    return by_userid


def _load_process_signature_bindings(process_code: str) -> dict[str, dict]:
    cfg = _cfg()
    path = cfg.base_dir / "data" / "process_signature_bindings.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    row = data.get(str(process_code or "").strip(), {}) if isinstance(data, dict) else {}
    bindings = row.get("bindings", {}) if isinstance(row, dict) else {}
    return bindings if isinstance(bindings, dict) else {}


def _slot_key(value) -> str:
    try:
        if value is None or value == "":
            return ""
        return str(int(float(value)))
    except Exception:
        return str(value or "").strip()


def _build_approver_slots(instance: dict, ding: DingTalkService) -> list[dict]:
    """
    Build signature/dept binding slots from the workflow's own signature data.

    Principle:
      - Flow signature data identifies the signer whenever DingTalk provides userid/name.
      - Local users.json is the source of truth for department/user correction.
      - Do not use DingTalk online user/department lookup here.
      - Do not globally bind people to template slots; slots belong to the current flow/template only.
    """
    local_by_userid, local_by_name = _load_local_users_indexes()

    def _local_by_signature(sig: dict) -> dict:
        uid = str(sig.get("userid") or "").strip()
        if uid and uid in local_by_userid:
            return local_by_userid[uid]
        name = str(sig.get("name") or "").strip()
        if name:
            matches = [u for u in local_by_name.get(name, []) if u.get("is_active", True)]
            if len(matches) == 1:
                return matches[0]
            matches = local_by_name.get(name, [])
            if len(matches) == 1:
                return matches[0]
        return {}

    slots: list[dict] = []
    slot_index = 1
    for comp in (instance or {}).get("form_component_values", []) or []:
        if not isinstance(comp, dict):
            continue
        ctype = str(comp.get("component_type") or "").strip()
        if ctype not in ("SignatureField", "DDSingleSign", "DDSign", "DDAttachmentSign"):
            continue
        comp_id = str(comp.get("id") or "").strip()
        comp_name = str(comp.get("name") or "").strip()
        sig_items = _extract_signature_items_from_component_value(comp.get("value"))
        for sig in sig_items:
            url = str(sig.get("url") or "").strip()
            if not url:
                continue
            local = _local_by_signature(sig)
            uid = str((local or {}).get("userid") or sig.get("userid") or "").strip()
            uname = str((local or {}).get("name") or sig.get("name") or comp_name or "").strip()
            dept_name = str((local or {}).get("dept_name") or "").strip()
            dept_path_name = str((local or {}).get("dept_path_name") or dept_name or "").strip()
            slots.append({
                "slot_index": slot_index,
                "userid": uid,
                "user_name": uname,
                "finish_time": "",
                "signature_url": url,
                "dept_name": dept_name,
                "dept_path_name": dept_path_name,
                "component_id": comp_id,
                "component_name": comp_name,
                "signature_data_id": str(sig.get("data_id") or "").strip(),
                "local_user_linked": bool(local),
            })
            slot_index += 1
    return slots


def _process_group_label(p: dict) -> str:
    """Best-effort folder name from DingTalk listbyuserid item; else 未分组."""
    if not isinstance(p, dict):
        return "未分组"
    for k in (
        "dirName",
        "dir_name",
        "group_name",
        "groupName",
        "process_group_name",
        "processGroupName",
        "folder_name",
        "folderName",
        "biz_category_name",
        "bizCategoryName",
        "process_category_name",
        "category_name",
        "flow_group_name",
        "biz_dir_name",
        "bizDirName",
    ):
        v = p.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return "未分组"


@designer_bp.route("/designer/api/processes_grouped")
def designer_processes_grouped():
    """
    分页拉取钉钉「审批表单」列表（按 next_cursor 全量分页），并按返回字段聚合成两级结构。
    - scope=corp（默认）：不传 userid，拉企业下表单（通常多于仅本人可见）。
    - scope=user：必须传 userid（或配置 DINGTALK_ADMIN_USERID），只拉该用户可见表单。
    """
    scope = str(request.args.get("scope") or "corp").strip().lower()
    user_arg = str(request.args.get("userid") or os.getenv("DINGTALK_ADMIN_USERID") or "").strip()
    if scope == "user" and not user_arg:
        return jsonify({"ok": False, "msg": "scope=user 时需要 userid 或配置 DINGTALK_ADMIN_USERID", "groups": []}), 400
    uid = user_arg if scope == "user" else None
    ding = _ding()
    try:
        procs, capped, list_backend = ding.list_all_approval_templates(userid=uid, page_size=100, max_pages=500)
    except DingTalkError as exc:
        return jsonify({"ok": False, "msg": str(exc), "groups": []}), 400

    group_hint = (
        "分组来自钉钉开放平台 dirName。"
        if list_backend == "openapi"
        else "当前使用旧版 listbyuserid（无目录字段）。请在应用权限中开通「工作流模板读」后刷新，方可显示与钉钉控制台一致的分组。"
    )

    groups_map: dict[str, list] = {}
    for p in procs:
        gname = _process_group_label(p)
        code = DingTalkService.normalize_code(p.get("process_code") or p.get("processCode") or "")
        if not code:
            continue
        name = str(p.get("name") or p.get("process_name") or code).strip()
        groups_map.setdefault(gname, []).append({"process_code": code, "name": name})

    groups = []
    for gn, items in groups_map.items():
        by_code: dict[str, dict] = {}
        for it in items:
            by_code[it["process_code"]] = it
        sorted_items = sorted(by_code.values(), key=lambda x: (x["name"].lower(), x["process_code"]))
        groups.append({"name": gn, "processes": sorted_items})
    groups.sort(key=lambda x: (1 if x["name"] == "未分组" else 0, x["name"].lower()))
    total = sum(len(g["processes"]) for g in groups)
    return jsonify(
        {
            "ok": True,
            "groups": groups,
            "total": total,
            "capped": capped,
            "scope": scope,
            "list_backend": list_backend,
            "group_hint": group_hint,
        }
    )


def _draw_text_with_spacing(
    *,
    fitz_mod,
    page,
    rect,
    text: str,
    fontname: str,
    fontsize: float,
    color,
    align: int,
    line_height: float,
    letter_spacing: float,
    overflow_marker: bool = True,
    text_wrap: bool = False,
    fontfile: str | None = None,
    vertical_align: str = "middle",  # 新增：纵向对齐 top, middle, bottom
):
    """
    Approximate text layout with line-height and letter-spacing.
    - align: 0 left, 1 center, 2 right (横向对齐)
    - vertical_align: top, middle, bottom (纵向对齐)
    - line_height: multiplier, e.g. 1.2
    - letter_spacing: pt between characters
    - text_wrap: if True, enable automatic line wrapping
    """
    content = str(text or "")
    if not content:
        return
    if not content:
        return
    lh = max(1.0, float(line_height or 1.2))
    ls = float(letter_spacing or 0.0)
    line_step = fontsize * lh

    def line_width(line: str) -> float:
        if not line:
            return 0.0
        base = _text_len(fitz_mod, line, fontname, fontsize)
        if ls > 0:
            base += (max(0, len(line) - 1)) * ls
        return base

    def wrap_line(src: str):
        s = src or ""
        if not s:
            return [""]
        # If text_wrap is disabled, return single line
        if not text_wrap:
            return [s]
        lines = []
        cur = ""
        for ch in s:
            nxt = cur + ch
            if line_width(nxt) <= rect.width - 1:
                cur = nxt
            else:
                if cur:
                    lines.append(cur)
                    cur = ch
                else:
                    # extremely narrow box: force one char per line
                    lines.append(ch)
                    cur = ""
        if cur:
            lines.append(cur)
        return lines if lines else [""]

    # hard line breaks + auto wrap
    raw_lines = content.splitlines() or [content]
    lines = []
    for ln in raw_lines:
        lines.extend(wrap_line(ln))
    if not lines:
        return

    max_lines = max(1, int(rect.height // line_step))
    original_line_count = len(lines)
    lines = lines[:max_lines]
    truncated = original_line_count > max_lines

    def fit_with_ellipsis(src: str) -> str:
        if not overflow_marker:
            return src
        ell = "..."
        src_width = line_width(src)
        ell_width = line_width(ell)
        src_ell_width = line_width(src + ell)
        
        # 调试信息
        print(f"[DEBUG] fit_with_ellipsis:")
        print(f"  text: '{src}'")
        print(f"  rect.width: {rect.width}")
        print(f"  src_width: {src_width}")
        print(f"  ell_width: {ell_width}")
        print(f"  src_ell_width: {src_ell_width}")
        
        # Keep trying to append ellipsis within width.
        if src_ell_width <= rect.width - 1:
            return src + ell
        # 如果控件太窄，连省略号都放不下，直接返回原文本
        if ell_width > rect.width - 1:
            print(f"[DEBUG] 控件太窄，返回原文本")
            return src
        s = src
        while s:
            s = s[:-1]
            if line_width(s + ell) <= rect.width - 1:
                print(f"[DEBUG] 截断为: '{s + ell}'")
                return s + ell
        # If space is very narrow, return ellipsis only if possible.
        result = ell if ell_width <= rect.width - 1 else src
        print(f"[DEBUG] 最终返回: '{result}'")
        return result

    for i, line in enumerate(lines):
        # 计算纵向对齐偏移
        total_text_height = len(lines) * line_step
        if vertical_align == "top":
            vertical_offset = 0
        elif vertical_align == "bottom":
            vertical_offset = max(0, rect.height - total_text_height)
        else:  # middle (默认)
            vertical_offset = max(0, (rect.height - total_text_height) / 2.0)
        
        y = rect.y0 + fontsize + vertical_offset + i * line_step
        if y > rect.y1:
            break
        if truncated and i == len(lines) - 1:
            line = fit_with_ellipsis(line)
        lw = line_width(line)
        if align == 1:
            x0 = rect.x0 + max(0, (rect.width - lw) / 2.0)
        elif align == 2:
            x0 = rect.x1 - lw
        else:
            x0 = rect.x0
        x = x0
        if ls <= 0:
            page.insert_text(
                fitz_mod.Point(x, y),
                line,
                fontsize=fontsize,
                fontname=fontname,
                fontfile=fontfile,
                color=color,
                overlay=True,
            )
        else:
            for ch in line:
                page.insert_text(
                    fitz_mod.Point(x, y),
                    ch,
                    fontsize=fontsize,
                    fontname=fontname,
                    fontfile=fontfile,
                    color=color,
                    overlay=True,
                )
                x += _text_len(fitz_mod, ch, fontname, fontsize) + ls


@designer_bp.route("/designer")
def designer_list():
    layouts = _load_layouts()
    return render_template("designer_list.html", layouts=layouts)


@designer_bp.route("/designer/edit")
def designer_edit():
    code = str(request.args.get("code") or "").strip()
    cfg = _cfg()
    layouts = _load_layouts()
    layout = layouts.get(code, {}) if code else {}
    return render_template(
        "designer_edit.html",
        code=code,
        layout=layout,
        all_templates=list_pdf_templates(cfg),
    )


@designer_bp.route("/designer/api/schema")
def designer_schema():
    process_code = str(request.args.get("process_code") or "").strip()
    req_code_norm = DingTalkService.normalize_code(process_code)
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code", "fields": []}), 400

    ding = _ding()
    userid = str(request.args.get("userid") or os.getenv("DINGTALK_ADMIN_USERID") or "").strip()
    if not userid:
        return jsonify({"ok": False, "msg": "缺少 userid（可配置 DINGTALK_ADMIN_USERID）", "fields": []}), 400

    instance_id = str(request.args.get("instance_id") or "").strip()
    try:
        if not instance_id:
            ids = ding.list_process_instance_ids(process_code, userid, size=1)
            if not ids:
                return jsonify({"ok": False, "msg": "未找到流程实例", "fields": []}), 404
            instance_id = ids[0]
        instance = ding.get_process_instance(instance_id)
    except DingTalkError as exc:
        return jsonify({"ok": False, "msg": str(exc), "fields": []}), 400
    ins_code_norm = _instance_process_code(instance)
    if req_code_norm and ins_code_norm and req_code_norm != ins_code_norm:
        return (
            jsonify(
                {
                    "ok": False,
                    "msg": f"实例与流程不匹配：instance_id={instance_id} 属于 {ins_code_norm}，当前流程是 {req_code_norm}",
                    "fields": [],
                }
            ),
            400,
        )

    fields = []
    for comp in (instance or {}).get("form_component_values", []) or []:
        if not isinstance(comp, dict):
            continue
        val = comp.get("value")
        if isinstance(val, str) and len(val) > 180:
            val_preview = val[:180] + "..."
        else:
            val_preview = val
        fields.append(
            {
                "id": str(comp.get("id") or ""),
                "name": str(comp.get("name") or ""),
                "type": str(comp.get("component_type") or ""),
                "value_preview": val_preview,
            }
        )
    system_fields = _build_system_fields(instance, process_code, instance_id)
    return jsonify({"ok": True, "instance_id": instance_id, "fields": fields, "system_fields": system_fields})


@designer_bp.route("/designer/api/nodes")
def designer_nodes():
    process_code = str(request.args.get("process_code") or "").strip()
    req_code_norm = DingTalkService.normalize_code(process_code)
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code", "nodes": []}), 400

    ding = _ding()
    userid = str(request.args.get("userid") or os.getenv("DINGTALK_ADMIN_USERID") or "").strip()
    if not userid:
        return jsonify({"ok": False, "msg": "缺少 userid（可配置 DINGTALK_ADMIN_USERID）", "nodes": []}), 400

    instance_id = str(request.args.get("instance_id") or "").strip()
    try:
        if not instance_id:
            ids = ding.list_process_instance_ids(process_code, userid, size=1)
            if not ids:
                return jsonify({"ok": False, "msg": "未找到流程实例", "nodes": []}), 404
            instance_id = ids[0]
        instance = ding.get_process_instance(instance_id)
    except DingTalkError as exc:
        return jsonify({"ok": False, "msg": str(exc), "nodes": []}), 400
    ins_code_norm = _instance_process_code(instance)
    if req_code_norm and ins_code_norm and req_code_norm != ins_code_norm:
        return (
            jsonify(
                {
                    "ok": False,
                    "msg": f"实例与流程不匹配：instance_id={instance_id} 属于 {ins_code_norm}，当前流程是 {req_code_norm}",
                    "nodes": [],
                }
            ),
            400,
        )

    tasks = (instance or {}).get("tasks", []) or []
    node_name_map_all = _load_node_name_map()
    process_node_map = node_name_map_all.get(process_code, {}) if isinstance(node_name_map_all, dict) else {}
    if not isinstance(process_node_map, dict):
        process_node_map = {}
    out = []
    for t in tasks:
        if not isinstance(t, dict):
            continue
        activity_id = str(t.get("activity_id") or "").strip()
        out.append(
            {
                "activity_id": activity_id,
                "activity_name": str(process_node_map.get(activity_id) or "").strip(),
                "taskid": str(t.get("taskid") or "").strip(),
                "userid": str(t.get("userid") or "").strip(),
                "task_status": str(t.get("task_status") or "").strip(),
                "task_result": str(t.get("task_result") or "").strip(),
                "create_time": str(t.get("create_time") or "").strip(),
                "finish_time": str(t.get("finish_time") or "").strip(),
                "url": str(t.get("url") or "").strip(),
            }
        )
    out.sort(key=lambda x: (x.get("activity_id") or "", x.get("finish_time") or "", x.get("taskid") or ""))
    return jsonify({"ok": True, "instance_id": instance_id, "nodes": out})


@designer_bp.route("/designer/api/pdf_meta")
def designer_pdf_meta():
    cfg = _cfg()
    base_pdf = str(request.args.get("base_pdf") or "").strip()
    if not base_pdf:
        return jsonify({"ok": False, "msg": "缺少 base_pdf"}), 400
    pdf_path = cfg.pdf_template_dir / base_pdf
    if not pdf_path.exists():
        return jsonify({"ok": False, "msg": "底稿不存在"}), 404

    import fitz

    try:
        doc = fitz.open(str(pdf_path))
        try:
            if doc.page_count <= 0:
                return jsonify({"ok": False, "msg": "PDF 无页面"}), 400
            page = doc[0]
            w = float(page.rect.width)
            h = float(page.rect.height)
            rot = int(getattr(page, "rotation", 0) or 0) % 360
            # visual size after applying page rotation
            if rot in (90, 270):
                vw, vh = h, w
            else:
                vw, vh = w, h
            orient = "l" if vw >= vh else "p"
            return jsonify(
                {
                    "ok": True,
                    "base_pdf": base_pdf,
                    "page_count": int(doc.page_count),
                    "first_page": {
                        "width": w,
                        "height": h,
                        "rotation": rot,
                        "view_width": vw,
                        "view_height": vh,
                        "orient": orient,
                    },
                }
            )
        finally:
            doc.close()
    except Exception as exc:
        return jsonify({"ok": False, "msg": f"读取 PDF 元信息失败: {exc}"}), 400


@designer_bp.route("/designer/api/node_names", methods=["GET", "POST"])
def designer_node_names():
    process_code = str((request.values.get("process_code") if request.method == "POST" else request.args.get("process_code")) or "").strip()
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code"}), 400

    all_map = _load_node_name_map()
    if not isinstance(all_map, dict):
        all_map = {}

    if request.method == "GET":
        curr = all_map.get(process_code, {})
        if not isinstance(curr, dict):
            curr = {}
        return jsonify({"ok": True, "process_code": process_code, "node_names": curr})

    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        payload = {}
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
    return jsonify({"ok": True, "msg": "保存成功", "process_code": process_code, "node_names": clean})


@designer_bp.route("/designer/api/stamp/fetch", methods=["POST"])
def designer_stamp_fetch():
    cfg = _cfg()
    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        payload = {}
    url = str(payload.get("url") or "").strip()
    key = str(payload.get("key") or "agree").strip().lower()
    pack = str(payload.get("pack") or "default").strip().lower()
    if pack not in ("default", "web", "client"):
        pack = "default"
    if not url.startswith("http://") and not url.startswith("https://"):
        return jsonify({"ok": False, "msg": "url 必须是 http(s)"}), 400
    if key not in ("agree", "refuse", "revoke", "pending"):
        key = "agree"
    try:
        res = _ding().session.get(url, timeout=cfg.request_timeout_seconds)
        if res.status_code != 200 or not res.content:
            return jsonify({"ok": False, "msg": "下载失败"}), 400
    except Exception as exc:
        return jsonify({"ok": False, "msg": f"下载异常: {exc}"}), 400

    stamp_dir = cfg.base_dir / "static" / "stamps"
    if pack != "default":
        stamp_dir = stamp_dir / pack
    stamp_dir.mkdir(parents=True, exist_ok=True)
    out = stamp_dir / f"{key}.png"
    out.write_bytes(res.content)

    assets = _load_stamp_assets()
    rel = f"static/stamps/{key}.png" if pack == "default" else f"static/stamps/{pack}/{key}.png"
    assets[f"{pack}:{key}"] = rel
    if pack == "default":
        assets[key] = rel
    _save_stamp_assets(assets)
    return jsonify({"ok": True, "key": key, "pack": pack, "path": str(out)})


@designer_bp.route("/designer/api/qr/backfill", methods=["GET", "POST"])
def designer_qr_backfill():
    if request.method == "GET":
        instance_id = str(request.args.get("instance_id") or "").strip()
        data = _load_instance_qr_map()
        if not instance_id:
            return jsonify({"ok": True, "count": len(data), "items": data})
        row = data.get(instance_id, {}) if isinstance(data, dict) else {}
        return jsonify({"ok": True, "instance_id": instance_id, "item": row if isinstance(row, dict) else {}})

    try:
        payload = request.get_json(force=True) or {}
    except Exception:
        payload = {}
    instance_id = str(payload.get("instance_id") or "").strip()
    qr_url = str(payload.get("qr_url") or "").strip()
    if not instance_id:
        return jsonify({"ok": False, "msg": "缺少 instance_id"}), 400
    if not qr_url:
        return jsonify({"ok": False, "msg": "缺少 qr_url"}), 400
    if not (qr_url.startswith("http://") or qr_url.startswith("https://")):
        return jsonify({"ok": False, "msg": "qr_url 必须是 http(s)"}), 400

    ding = _ding()
    try:
        instance = ding.get_process_instance(instance_id)
    except DingTalkError as exc:
        return jsonify({"ok": False, "msg": str(exc)}), 400
    ins_pc = _instance_process_code(instance)
    payload_pc = DingTalkService.normalize_code(str(payload.get("process_code") or "").strip())
    if payload_pc and ins_pc and payload_pc != ins_pc:
        return jsonify({"ok": False, "msg": f"process_code 与实例不符：该实例属于 {ins_pc}"}), 400
    store_pc = payload_pc or ins_pc
    business_id = str(instance.get("business_id") or "").strip()

    data = _load_instance_qr_map()
    if not isinstance(data, dict):
        data = {}
    data[instance_id] = {
        "qr_url": qr_url,
        "process_code": store_pc,
        "business_id": business_id,
        "source": str(payload.get("source") or "manual").strip() or "manual",
        "updated_at": datetime.utcnow().isoformat(),
    }
    _save_instance_qr_map(data)
    return jsonify({"ok": True, "instance_id": instance_id, "item": data[instance_id]})


@designer_bp.route("/designer/api/preview", methods=["POST", "GET"])
def designer_preview():
    """
    Minimal preview:
    - Open selected base_pdf (first page for now)
    - Draw layout items as overlay:
        - text/label/date: insert_textbox (helv)
        - signature: download image from SignatureField value and insert_image (keep ratio by PDF engine)
        - rect/line: draw shapes
    """
    cfg = _cfg()
    ding = _ding()

    try:
        if request.method == "POST":
            payload = request.get_json(force=True) or {}
        else:  # GET
            # 从查询参数中获取数据
            payload = {}
            for key in request.args:
                value = request.args.get(key)
                # 尝试解析 JSON 字符串
                if key in ('items', 'attachment_background_config'):
                    try:
                        payload[key] = json.loads(value)
                    except:
                        payload[key] = value
                elif key == 'use_template':
                    payload[key] = value in ('1', 'true', 'True')
                elif key in ('cover_offset_x', 'cover_offset_y'):
                    try:
                        payload[key] = float(value)
                    except:
                        payload[key] = 0
                else:
                    payload[key] = value
    except Exception:
        payload = {}
    process_code = str(payload.get("process_code") or "").strip()
    req_code_norm = DingTalkService.normalize_code(process_code)
    base_pdf = str(payload.get("base_pdf") or "").strip()
    use_template = bool(payload.get("use_template", True))
    orientation = str(payload.get("orientation") or "l").strip().lower()
    if orientation not in ("l", "p"):
        orientation = "l"
    cover_source_mode = str(payload.get("cover_source_mode") or "base").strip().lower()
    if cover_source_mode not in ("base", "attachment"):
        cover_source_mode = "base"
    cover_mode = str(payload.get("cover_mode") or "strict").strip().lower()
    if cover_mode not in ("strict", "fit", "fit_offset"):
        cover_mode = "strict"
    try:
        cover_offset_x = float(payload.get("cover_offset_x") or 0)
    except Exception:
        cover_offset_x = 0.0
    try:
        cover_offset_y = float(payload.get("cover_offset_y") or 0)
    except Exception:
        cover_offset_y = 0.0
    
    # 读取附件底图配置
    attachment_bg_config = payload.get("attachment_background_config") or {}
    attachment_bg_enabled = attachment_bg_config.get("enabled", False)
    attachment_bg_field_id = str(attachment_bg_config.get("field_id") or "").strip()
    attachment_bg_index = int(attachment_bg_config.get("attachment_index") or 0)
    attachment_bg_page = int(attachment_bg_config.get("page_index") or 0)
    attachment_bg_apply_mode = str(attachment_bg_config.get("apply_mode") or "print_only").strip()
    
    items = payload.get("items") or []
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code"}), 400
    
    # 检查是否使用附件底图
    using_attachment_bg = (
        cover_source_mode == "attachment" 
        and attachment_bg_enabled 
        and attachment_bg_field_id
    )
    
    # 如果使用模板但不是附件底图，需要 base_pdf
    if use_template and not using_attachment_bg and not base_pdf:
        return jsonify({"ok": False, "msg": "缺少 base_pdf"}), 400
    
    # 如果使用附件底图但没有 base_pdf，根据方向使用对应的空白模板
    if using_attachment_bg and not base_pdf:
        if orientation == "p":
            base_pdf = "blank_portrait.pdf"  # 纵向空白模板
        else:
            base_pdf = "blank_landscape.pdf"  # 横向空白模板
    
    if not isinstance(items, list):
        return jsonify({"ok": False, "msg": "items 必须是数组"}), 400
    # Force fixed portrait status-stamp (cannot be deleted by frontend operations).
    if orientation == "p":
        fixed_id = "__fixed_status_stamp_portrait"
        filtered = []
        for it in items:
            if isinstance(it, dict) and str(it.get("id") or "") == fixed_id:
                continue
            filtered.append(it)
        filtered.append(
            {
                "id": fixed_id,
                "locked": True,
                "renderer": "status_stamp",
                "label": "状态章",
                "page": 0,
                "x": 450,
                "y": 80,
                "w": 70,
                "h": 70,
                "stamp_status": "auto",
                "stamp_pack": "client",
            }
        )
        items = filtered

    userid = str(payload.get("userid") or os.getenv("DINGTALK_ADMIN_USERID") or "").strip()
    if not userid:
        return jsonify({"ok": False, "msg": "缺少 userid（可配置 DINGTALK_ADMIN_USERID）"}), 400

    instance_id = str(payload.get("instance_id") or "").strip()
    try:
        if not instance_id:
            ids = ding.list_process_instance_ids(process_code, userid, size=1)
            if not ids:
                return jsonify({"ok": False, "msg": "未找到流程实例"}), 404
            instance_id = ids[0]
        instance = ding.get_process_instance(instance_id)
    except DingTalkError as exc:
        return jsonify({"ok": False, "msg": str(exc)}), 400
    ins_code_norm = _instance_process_code(instance)
    if req_code_norm and ins_code_norm and req_code_norm != ins_code_norm:
        return (
            jsonify(
                {
                    "ok": False,
                    "msg": f"实例与流程不匹配：instance_id={instance_id} 属于 {ins_code_norm}，当前流程是 {req_code_norm}",
                }
            ),
            400,
        )

    # build form field map
    field_map = {}
    for comp in (instance or {}).get("form_component_values", []) or []:
        if isinstance(comp, dict):
            field_map[str(comp.get("id") or "")] = comp
    # build system field map
    system_value_map = {}
    for sf in _build_system_fields(instance, process_code, instance_id):
        if isinstance(sf, dict):
            system_value_map[str(sf.get("id") or "")] = str(sf.get("value") or sf.get("value_preview") or "")
    approver_slots = _build_approver_slots(instance, ding)
    approver_slots_by_field_id = {
        str(slot.get("component_id") or "").strip(): slot
        for slot in approver_slots
        if str(slot.get("component_id") or "").strip()
    }

    def _slot_for_layout_item(layout_item: dict) -> dict:
        field_id = str((layout_item or {}).get("field_id") or "").strip()
        if field_id and field_id in approver_slots_by_field_id:
            return approver_slots_by_field_id[field_id]
        try:
            slot_index = max(1, int(float((layout_item or {}).get("slot_index") or 1)))
        except Exception:
            slot_index = 1
        return approver_slots[slot_index - 1] if 0 <= (slot_index - 1) < len(approver_slots) else {}

    local_users_by_id, local_users_by_name = _load_local_users_indexes()
    process_signature_bindings = _load_process_signature_bindings(req_code_norm or process_code)
    form_components_by_id = {
        str(comp.get("id") or "").strip(): comp
        for comp in (instance or {}).get("form_component_values", []) or []
        if isinstance(comp, dict) and str(comp.get("id") or "").strip()
    }

    def _local_user_by_name_value(raw_value) -> dict:
        raw = raw_value
        if isinstance(raw, str):
            s = raw.strip()
            if (s.startswith("[") or s.startswith("{")):
                try:
                    raw = json.loads(s)
                except Exception:
                    raw = s
            else:
                raw = s
        names: list[str] = []
        userids: list[str] = []
        def walk(v):
            if isinstance(v, dict):
                for k in ("userid", "userId", "staffId", "staff_id"):
                    val = str(v.get(k) or "").strip()
                    if val:
                        userids.append(val)
                for k in ("name", "userName", "user_name", "label", "nick"):
                    val = str(v.get(k) or "").strip()
                    if val:
                        names.append(val)
                for child in v.values():
                    if isinstance(child, (dict, list)):
                        walk(child)
            elif isinstance(v, list):
                for child in v:
                    walk(child)
            else:
                s = str(v or "").strip()
                if s:
                    for part in re.split(r"[,，;；/、\\s]+", s):
                        p = part.strip()
                        if p:
                            names.append(p)
        walk(raw)
        for uid in userids:
            if uid in local_users_by_id:
                return local_users_by_id[uid]
        for name in names:
            matches = [u for u in local_users_by_name.get(name, []) if u.get("is_active", True)]
            if len(matches) == 1:
                return matches[0]
            matches = local_users_by_name.get(name, [])
            if len(matches) == 1:
                return matches[0]
        return {}

    def _local_user_for_binding(binding: dict) -> dict:
        source_type = str((binding or {}).get("source_type") or "").strip()
        if source_type == "form_field":
            source_field_id = str((binding or {}).get("source_field_id") or "").strip()
            comp = form_components_by_id.get(source_field_id, {})
            if comp:
                user = _local_user_by_name_value(comp.get("value"))
                if user:
                    return user
        uid = str((binding or {}).get("local_userid") or "").strip()
        if uid and uid in local_users_by_id:
            return local_users_by_id[uid]
        name = str((binding or {}).get("local_user_name") or "").strip()
        if name:
            return _local_user_by_name_value(name)
        return {}

    def _local_user_for_layout_item(layout_item: dict) -> dict:
        field_id = str((layout_item or {}).get("field_id") or "").strip()
        binding = process_signature_bindings.get(field_id, {}) if field_id else {}
        binding_user = _local_user_for_binding(binding)
        if binding_user:
            return binding_user
        uid = str((layout_item or {}).get("local_userid") or (layout_item or {}).get("local_user_id") or "").strip()
        if uid and uid in local_users_by_id:
            return local_users_by_id[uid]
        name = str((layout_item or {}).get("local_user_name") or "").strip()
        if name:
            matches = [u for u in local_users_by_name.get(name, []) if u.get("is_active", True)]
            if len(matches) == 1:
                return matches[0]
            matches = local_users_by_name.get(name, [])
            if len(matches) == 1:
                return matches[0]
        return {}

    import fitz  # local import
    from io import BytesIO
    import time as _time

    src_doc = None
    if use_template:
        pdf_path = cfg.pdf_template_dir / base_pdf
        
        # 检查文件是否存在（但如果使用附件底图，即使文件不存在也继续）
        if not pdf_path.exists():
            # 如果使用附件底图，文件不存在也没关系（会用附件替代）
            if not (cover_source_mode == "attachment" and attachment_bg_enabled and attachment_bg_field_id):
                return jsonify({"ok": False, "msg": f"底稿不存在: {base_pdf}"}), 404

        # Pick preview background source: base template or process attachment.
        source_pdf_bytes = None
        print(f"[DEBUG] ===== 开始处理附件底图 =====")
        print(f"[DEBUG] cover_source_mode: '{cover_source_mode}'")
        print(f"[DEBUG] cover_source_mode == 'attachment': {cover_source_mode == 'attachment'}")
        
        if cover_source_mode == "attachment":
            print(f"[DEBUG] ✅ 进入 attachment 分支")
            print(f"[DEBUG] attachment_bg_enabled: {attachment_bg_enabled}")
            print(f"[DEBUG] attachment_bg_field_id: {attachment_bg_field_id}")
            print(f"[DEBUG] attachment_bg_apply_mode: {attachment_bg_apply_mode}")
            
            # 如果配置了附件底图，使用指定的字段和索引
            if attachment_bg_enabled and attachment_bg_field_id:
                # 检查应用模式：preview_and_print, preview_only, print_only
                should_apply = (
                    attachment_bg_apply_mode in ("preview_and_print", "preview_only", "both") or
                    not attachment_bg_apply_mode  # 默认应用
                )
                print(f"[DEBUG] should_apply: {should_apply}")
                
                if should_apply:
                    print(f"[DEBUG] 尝试下载附件: field_id={attachment_bg_field_id}, index={attachment_bg_index}")
                    # 使用配置中指定的附件字段
                    source_pdf_bytes = ding.download_specific_attachment_pdf(
                        instance=instance,
                        field_id=attachment_bg_field_id,
                        attachment_index=attachment_bg_index
                    )
                    if source_pdf_bytes:
                        print(f"[DEBUG] ✅ 附件下载成功，大小: {len(source_pdf_bytes)} bytes")
                    else:
                        print(f"[DEBUG] ❌ 附件下载失败或为空")
            
            # 如果没有获取到附件，兼容旧逻辑：自动查找第一个 PDF 附件
            if not source_pdf_bytes:
                print(f"[DEBUG] 尝试兜底逻辑：自动查找第一个 PDF 附件")
                source_pdf_bytes = ding.download_process_attachment_pdf(process_instance_id=instance_id, instance=instance)
                if source_pdf_bytes:
                    print(f"[DEBUG] ✅ 兜底逻辑成功，大小: {len(source_pdf_bytes)} bytes")
        else:
            print(f"[DEBUG] ❌ 未进入 attachment 分支，cover_source_mode = '{cover_source_mode}'")
        
        if source_pdf_bytes:
            print(f"[DEBUG] 使用附件 PDF 作为底图")
            src_doc = fitz.open(stream=source_pdf_bytes, filetype="pdf")
            # 如果指定了页码，只使用指定的页
            if cover_source_mode == "attachment" and attachment_bg_enabled and attachment_bg_page >= 0:
                if attachment_bg_page < src_doc.page_count:
                    # 创建只包含指定页的临时文档
                    temp_doc = fitz.open()
                    temp_doc.insert_pdf(src_doc, from_page=attachment_bg_page, to_page=attachment_bg_page)
                    src_doc.close()
                    src_doc = temp_doc
        else:
            src_doc = fitz.open(str(pdf_path))
    doc = None
    try:
        # Plan A:
        # - Do not mutate source PDF page rotation.
        # - Build a fresh preview document in target orientation (A4 l/p).
        # - Draw source pages into target pages, then overlay layout items directly
        #   in this stable coordinate space.
        desired_orient = "l" if orientation == "l" else "p"
        target_w, target_h = ((842.0, 595.0) if desired_orient == "l" else (595.0, 842.0))
        doc = fitz.open()
        # Render base template as stretched PNG per target orientation.
        # This keeps template background non-rotated in all cases.
        if use_template and src_doc is not None:
            for pidx in range(src_doc.page_count):
                p = doc.new_page(width=target_w, height=target_h)
                try:
                    if cover_source_mode == "attachment":
                        # 优化：提高渲染 DPI 以获得更清晰的图像
                        # 计算缩放矩阵，使用 2x 或 3x 分辨率
                        dpi_scale = 3.0  # 3倍分辨率，相当于 216 DPI
                        scale_x = (target_w / src_doc[pidx].rect.width) * dpi_scale
                        scale_y = (target_h / src_doc[pidx].rect.height) * dpi_scale
                        matrix = fitz.Matrix(scale_x, scale_y)
                        
                        print(f"[DEBUG] 渲染附件底图: DPI scale={dpi_scale}, matrix={matrix}")
                        
                        pix = src_doc[pidx].get_pixmap(matrix=matrix, alpha=False)
                        png_bytes = pix.tobytes("png")
                        
                        print(f"[DEBUG] 附件底图尺寸: {pix.width}x{pix.height}, 大小: {len(png_bytes)} bytes")
                    else:
                        png_bytes = render_pdf_page_png(cfg, base_pdf, pidx, desired_orient)
                    p.insert_image(fitz.Rect(0, 0, target_w, target_h), stream=png_bytes, keep_proportion=False, overlay=False)
                except Exception as e:
                    print(f"[ERROR] 渲染页面失败: {e}")
                    pass
        else:
            max_page = 0
            for it in items:
                if isinstance(it, dict):
                    try:
                        p = int(it.get("page", 0) or 0)
                        if p >= 0:
                            max_page = max(max_page, p)
                    except Exception:
                        pass
            for _ in range(max_page + 1):
                doc.new_page(width=target_w, height=target_h)

        for it in items:
            if not isinstance(it, dict):
                continue
            rtype = str(it.get("renderer") or "text").lower()
            page_idx = int(it.get("page", 0) or 0)
            if page_idx < 0:
                page_idx = doc.page_count + page_idx
            if not (0 <= page_idx < doc.page_count):
                continue
            page = doc[page_idx]
            x = float(it.get("x", 0))
            y = float(it.get("y", 0))
            w = float(it.get("w", 0))
            h = float(it.get("h", 0))
            if cover_mode in ("fit", "fit_offset"):
                ref_w, ref_h = ((842.0, 595.0) if orientation == "l" else (595.0, 842.0))
                sx = target_w / ref_w if ref_w else 1.0
                sy = target_h / ref_h if ref_h else 1.0
                x *= sx
                y *= sy
                w *= sx
                h *= sy
            if cover_mode == "fit_offset":
                x += cover_offset_x
                y += cover_offset_y
            rect = fitz.Rect(x, y, x + w, y + h)
            if rtype in ("rect",):
                sc_hex = str(it.get("stroke_color") or "#334155").strip()
                sw = float(it.get("stroke_width") or 0.8)
                rr = float(it.get("rect_radius") or 0.0)
                if sw <= 0:
                    sw = 0.8
                if rr < 0:
                    rr = 0.0
                sc = (0.2, 0.2, 0.35)
                if sc_hex.startswith("#") and len(sc_hex) == 7:
                    try:
                        sc = (
                            int(sc_hex[1:3], 16) / 255.0,
                            int(sc_hex[3:5], 16) / 255.0,
                            int(sc_hex[5:7], 16) / 255.0,
                        )
                    except Exception:
                        pass
                page.draw_rect(rect, color=sc, width=sw, radius=rr if rr > 0 else None)
                continue
            if rtype in ("line",):
                dirn = str(it.get("line_direction") or "horizontal").strip().lower()
                line_style = str(it.get("line_style") or "solid").strip().lower()
                sc_hex = str(it.get("stroke_color") or "#111827").strip()
                sw = float(it.get("stroke_width") or 1.0)
                if sw <= 0:
                    sw = 1.0
                sc = (0.0, 0.0, 0.0)
                if sc_hex.startswith("#") and len(sc_hex) == 7:
                    try:
                        sc = (
                            int(sc_hex[1:3], 16) / 255.0,
                            int(sc_hex[3:5], 16) / 255.0,
                            int(sc_hex[5:7], 16) / 255.0,
                        )
                    except Exception:
                        pass
                if dirn == "vertical":
                    x = rect.x0 + rect.width / 2
                    p0 = fitz.Point(x, rect.y0)
                    p1 = fitz.Point(x, rect.y1)
                else:
                    y = rect.y0 + rect.height / 2
                    p0 = fitz.Point(rect.x0, y)
                    p1 = fitz.Point(rect.x1, y)
                dash = "[3 2] 0" if line_style == "dashed" else None
                page.draw_line(p0, p1, color=sc, width=sw, dashes=dash)
                continue
            if rtype in ("image",):
                image_url = str(it.get("image_url") or "").strip()
                image_fit = str(it.get("image_fit") or "contain").strip().lower()
                image_bytes = b""
                if image_url.startswith("data:image/") and ";base64," in image_url:
                    try:
                        b64 = image_url.split(";base64,", 1)[1]
                        image_bytes = base64.b64decode(b64)
                    except Exception:
                        image_bytes = b""
                elif image_url.startswith("http://") or image_url.startswith("https://"):
                    try:
                        img_res = ding.session.get(image_url, timeout=cfg.request_timeout_seconds)
                        if img_res.status_code == 200:
                            image_bytes = img_res.content
                    except Exception:
                        image_bytes = b""
                if image_bytes:
                    try:
                        page.insert_image(
                            rect,
                            stream=image_bytes,
                            keep_proportion=(image_fit != "cover"),
                            overlay=True,
                        )
                    except Exception:
                        page.draw_rect(rect, color=(0.1, 0.6, 0.9), width=0.8)
                else:
                    page.draw_rect(rect, color=(0.1, 0.6, 0.9), width=0.8)
                continue
            if rtype in ("status_stamp",):
                stamp_status = str(it.get("stamp_status") or "auto").strip().lower()
                stamp_pack = str(it.get("stamp_pack") or "default").strip().lower()
                if stamp_pack not in ("default", "web", "client"):
                    stamp_pack = "default"
                if stamp_status == "auto":
                    raw = str((instance or {}).get("result") or (instance or {}).get("status") or "").strip().lower()
                    if raw in ("agree", "approved", "pass", "passed", "completed"):
                        stamp_status = "agree"
                    elif raw in ("refuse", "reject", "rejected"):
                        stamp_status = "refuse"
                    elif raw in ("revoke", "revoked", "cancel"):
                        stamp_status = "revoke"
                    else:
                        stamp_status = "pending"
                assets = _load_stamp_assets()
                rel = str(
                    assets.get(f"{stamp_pack}:{stamp_status}")
                    or assets.get(stamp_status)
                    or (f"static/stamps/{stamp_status}.png" if stamp_pack == "default" else f"static/stamps/{stamp_pack}/{stamp_status}.png")
                )
                stamp_path = _cfg().base_dir / rel
                if stamp_path.exists():
                    try:
                        page.insert_image(rect, filename=str(stamp_path), keep_proportion=True, rotate=0, overlay=True)
                    except Exception:
                        page.draw_rect(rect, color=(0.1, 0.7, 0.5), width=0.8)
                else:
                    page.draw_rect(rect, color=(0.1, 0.7, 0.5), width=0.8)
                continue
            if rtype in ("qrcode",):
                qr_source = str(it.get("qr_source") or "field").strip().lower()
                qr_value = ""
                if qr_source == "custom":
                    qr_value = str(it.get("qr_value") or "").strip()
                else:
                    field_id = str(it.get("field_id") or "").strip()
                    if field_id.startswith("sys."):
                        qr_value = str(system_value_map.get(field_id) or "").strip()
                    else:
                        comp = field_map.get(field_id) if field_id else None
                        if isinstance(comp, dict):
                            qr_value = str(comp.get("value") or "").strip()
                if qr_value:
                    try:
                        import qrcode
                        from io import BytesIO as _B

                        # DingTalk-like default: black/white with clear quiet-zone.
                        qr = qrcode.QRCode(
                            error_correction=qrcode.constants.ERROR_CORRECT_H,
                            border=4,
                            box_size=10,
                        )
                        qr.add_data(qr_value)
                        qr.make(fit=True)
                        qimg = qr.make_image(fill_color="black", back_color="white")
                        # Resize to target rect while preserving crisp blocks.
                        try:
                            from PIL import Image

                            rw = max(16, int(rect.width))
                            rh = max(16, int(rect.height))
                            qimg = qimg.resize((rw, rh), resample=Image.Resampling.NEAREST)
                        except Exception:
                            pass
                        bb = _B()
                        qimg.save(bb, format="PNG")
                        # Keep square proportions to avoid scan failures caused by distortion.
                        page.insert_image(rect, stream=bb.getvalue(), keep_proportion=True, rotate=0, overlay=True)
                    except Exception:
                        page.draw_rect(rect, color=(0.1, 0.1, 0.1), width=0.8)
                else:
                    page.draw_rect(rect, color=(0.1, 0.1, 0.1), width=0.8)
                continue

            if rtype in ("flow_result",):
                text, auto_color = _flow_result_text_and_color(instance)
                font_family = str(it.get("font_family") or "helv").strip().lower()
                if font_family not in ("helv", "china-s"):
                    font_family = "helv"
                font_style = str(it.get("font_style") or "normal").strip().lower()
                font_weight = str(it.get("font_weight") or "bold").strip().lower()
                fontname = font_family
                if font_family == "helv":
                    if font_weight == "bold" and font_style == "italic":
                        fontname = "hebi"
                    elif font_weight == "bold":
                        fontname = "hebo"
                    elif font_style == "italic":
                        fontname = "heit"
                    else:
                        fontname = "helv"
                fontsize = float(it.get("font_size") or 11)
                if fontsize <= 0:
                    fontsize = 11
                align_map = {"left": 0, "center": 1, "right": 2}
                align = align_map.get(str(it.get("text_align") or "left").lower(), 0)
                fontfile = None
                if _contains_cjk(text) and font_family in ("helv", "china-s"):
                    fontfile = _pick_designer_cjk_fontfile()
                    if fontfile:
                        fontname = "F0"
                # 获取纵向对齐方式
                vertical_align_map = {"top": "top", "middle": "middle", "bottom": "bottom"}
                vertical_align = vertical_align_map.get(str(it.get("vertical_align") or "middle").lower(), "middle")
                
                _draw_text_with_spacing(
                    fitz_mod=fitz,
                    page=page,
                    rect=rect,
                    text=text,
                    fontname=fontname,
                    fontsize=fontsize,
                    color=auto_color,
                    align=align,
                    line_height=float(it.get("line_height") or 1.2),
                    letter_spacing=float(it.get("letter_spacing") or 0.0),
                    overflow_marker=bool(it.get("overflow_marker", True)),
                    text_wrap=bool(it.get("text_wrap", False)),
                    fontfile=fontfile,
                    vertical_align=vertical_align,  # 新增
                )
                continue

            # text style (for text/date/label)
            font_family = str(it.get("font_family") or "helv").strip().lower()
            if font_family not in ("helv", "china-s"):
                font_family = "helv"
            font_style = str(it.get("font_style") or "normal").strip().lower()
            font_weight = str(it.get("font_weight") or "normal").strip().lower()
            fontname = font_family
            # Base-14 fallback variants for helv
            if font_family == "helv":
                if font_weight == "bold" and font_style == "italic":
                    fontname = "hebi"
                elif font_weight == "bold":
                    fontname = "hebo"
                elif font_style == "italic":
                    fontname = "heit"
                else:
                    fontname = "helv"
            fontsize = float(it.get("font_size") or 9)
            if fontsize <= 0:
                fontsize = 9
            color_hex = str(it.get("font_color") or "#000000").strip()
            color = (0.0, 0.0, 0.0)
            if color_hex.startswith("#") and len(color_hex) == 7:
                try:
                    r = int(color_hex[1:3], 16) / 255.0
                    g = int(color_hex[3:5], 16) / 255.0
                    b = int(color_hex[5:7], 16) / 255.0
                    color = (r, g, b)
                except Exception:
                    color = (0.0, 0.0, 0.0)
            align_map = {"left": 0, "center": 1, "right": 2}
            align = align_map.get(str(it.get("text_align") or "left").lower(), 0)
            fontfile = None

            field_id = str(it.get("field_id") or "").strip()
            comp = field_map.get(field_id) if field_id else None
            if rtype == "signature":
                sig_fill_mode = str(it.get("sig_fill_mode") or "manual").strip().lower()
                try:
                    slot_index = max(1, int(float(it.get("slot_index") or 1)))
                except Exception:
                    slot_index = 1
                if sig_fill_mode == "auto_sequence":
                    slot = _slot_for_layout_item(it)
                    url = str((slot or {}).get("signature_url") or "").strip()
                    if url:
                        try:
                            img_res = ding.session.get(url, timeout=cfg.request_timeout_seconds)
                            if img_res.status_code == 200:
                                page.insert_image(rect, stream=img_res.content, keep_proportion=True, rotate=0, overlay=True)
                            else:
                                page.draw_rect(rect, color=(0.8, 0.2, 0.2), width=0.6)
                        except Exception:
                            page.draw_rect(rect, color=(0.8, 0.2, 0.2), width=0.6)
                    else:
                        page.draw_rect(rect, color=(0.8, 0.2, 0.2), width=0.6)
                    continue
                url = ""
                if isinstance(comp, dict):
                    v = comp.get("value")
                    if isinstance(v, str) and v.startswith("http"):
                        url = v
                if url:
                    try:
                        img_res = ding.session.get(url, timeout=cfg.request_timeout_seconds)
                        if img_res.status_code == 200:
                            page.insert_image(rect, stream=img_res.content, keep_proportion=True, rotate=0, overlay=True)
                    except Exception:
                        pass
                else:
                    page.draw_rect(rect, color=(0.8, 0.2, 0.2), width=0.6)
                continue

            if rtype == "dept":
                try:
                    slot_index = max(1, int(float(it.get("slot_index") or 1)))
                except Exception:
                    slot_index = 1
                slot = _slot_for_layout_item(it)
                local_user = _local_user_for_layout_item(it)
                field_id = str((it or {}).get("field_id") or "").strip()
                binding = process_signature_bindings.get(field_id, {}) if field_id else {}
                text = str((local_user or {}).get("dept_name") or (binding or {}).get("dept_name") or (slot or {}).get("dept_name") or "").strip()
                empty_policy = str(it.get("empty_policy") or "show_placeholder").strip().lower()
                if not text and empty_policy == "hide":
                    continue
                if not text:
                    text = "未匹配部门"
                font_family = str(it.get("font_family") or "china-s").strip().lower()
                if font_family not in ("helv", "china-s"):
                    font_family = "china-s"
                font_style = str(it.get("font_style") or "normal").strip().lower()
                font_weight = str(it.get("font_weight") or "bold").strip().lower()
                fontname = font_family
                if font_family == "helv":
                    if font_weight == "bold" and font_style == "italic":
                        fontname = "hebi"
                    elif font_weight == "bold":
                        fontname = "hebo"
                    elif font_style == "italic":
                        fontname = "heit"
                    else:
                        fontname = "helv"
                fontsize = float(it.get("font_size") or 10)
                if fontsize <= 0:
                    fontsize = 10
                color_hex = str(it.get("font_color") or "#334155").strip()
                color = (0.2, 0.26, 0.33)
                if color_hex.startswith("#") and len(color_hex) == 7:
                    try:
                        color = (
                            int(color_hex[1:3], 16) / 255.0,
                            int(color_hex[3:5], 16) / 255.0,
                            int(color_hex[5:7], 16) / 255.0,
                        )
                    except Exception:
                        pass
                align_map = {"left": 0, "center": 1, "right": 2}
                align = align_map.get(str(it.get("text_align") or "left").lower(), 0)
                
                # 获取纵向对齐方式
                vertical_align_map = {"top": "top", "middle": "middle", "bottom": "bottom"}
                vertical_align = vertical_align_map.get(str(it.get("vertical_align") or "middle").lower(), "middle")
                
                fontfile = None
                if _contains_cjk(text):
                    fontfile = _pick_designer_cjk_fontfile()
                    if fontfile:
                        fontname = "F0"
                _draw_text_with_spacing(
                    fitz_mod=fitz,
                    page=page,
                    rect=rect,
                    text=text,
                    fontname=fontname,
                    fontsize=fontsize,
                    color=color,
                    align=align,
                    line_height=float(it.get("line_height") or 1.2),
                    letter_spacing=float(it.get("letter_spacing") or 0.0),
                    overflow_marker=bool(it.get("overflow_marker", True)),
                    text_wrap=bool(it.get("text_wrap", False)),
                    fontfile=fontfile,
                    vertical_align=vertical_align,  # 新增
                )
                continue

            text = str(it.get("label") or "").strip()
            print(f"[DEBUG] 处理控件: renderer={rtype}, label='{text}', field_id={field_id}")
            
            if field_id.startswith("sys."):
                text = str(system_value_map.get(field_id) or text or "")
            elif isinstance(comp, dict):
                v = comp.get("value")
                if rtype == "date":
                    text = str(v or "")
                elif text == "" or text == it.get("field_name"):
                    text = str(v or "")
            
            print(f"[DEBUG] 处理后文本: '{text}'")
            
            empty_policy = str(it.get("empty_policy") or "show_placeholder").strip().lower()
            if not text:
                print(f"[DEBUG] 文本为空, empty_policy={empty_policy}")
                if empty_policy == "hide":
                    continue
                if empty_policy == "dim":
                    color = (0.62, 0.65, 0.7)
            if text:
                print(f"[DEBUG] 准备渲染文本: '{text}', fontname={fontname}, fontsize={fontsize}")
                # Ensure Chinese labels/values don't become "???" with helv.
                if _contains_cjk(text) and font_family in ("helv", "china-s"):
                    fontfile = _pick_designer_cjk_fontfile()
                    if fontfile:
                        fontname = "F0"
                        print(f"[DEBUG] 使用中文字体: fontname=F0, fontfile={fontfile}")
                
                # 获取纵向对齐方式（只在文本渲染时使用）
                vertical_align_map = {"top": "top", "middle": "middle", "bottom": "bottom"}
                vertical_align = vertical_align_map.get(str(it.get("vertical_align") or "middle").lower(), "middle")
                
                _draw_text_with_spacing(
                    fitz_mod=fitz,
                    page=page,
                    rect=rect,
                    text=text,
                    fontname=fontname,
                    fontsize=fontsize,
                    color=color,
                    align=align,
                    line_height=float(it.get("line_height") or 1.2),
                    letter_spacing=float(it.get("letter_spacing") or 0.0),
                    overflow_marker=bool(it.get("overflow_marker", True)),
                    text_wrap=bool(it.get("text_wrap", False)),
                    fontfile=fontfile,
                    vertical_align=vertical_align,  # 新增
                )

        out = BytesIO()
        doc.save(out, garbage=4, clean=1, deflate=1, deflate_images=1, deflate_fonts=1, use_objstms=1)
        out.seek(0)
        return send_file(
            out,
            mimetype="application/pdf",
            download_name=f"preview_{process_code}_{desired_orient}_{int(_time.time()*1000)}.pdf",
        )
    finally:
        if doc is not None:
            doc.close()
        if src_doc is not None:
            src_doc.close()

@designer_bp.route("/designer/save", methods=["POST"])
def designer_save():
    process_code = str(request.form.get("process_code") or "").strip()
    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code"}), 400

    layout_name = str(request.form.get("name") or "").strip()
    base_pdf = str(request.form.get("base_pdf") or "").strip()
    use_template = str(request.form.get("use_template") or "1").strip() != "0"
    orientation = str(request.form.get("orientation") or "l").strip().lower()
    cover_source_mode = str(request.form.get("cover_source_mode") or "base").strip().lower()
    if cover_source_mode not in ("base", "attachment"):
        cover_source_mode = "base"
    cover_mode = str(request.form.get("cover_mode") or "strict").strip().lower()
    if cover_mode not in ("strict", "fit", "fit_offset"):
        cover_mode = "strict"
    try:
        cover_offset_x = float(request.form.get("cover_offset_x") or 0)
    except Exception:
        cover_offset_x = 0.0
    try:
        cover_offset_y = float(request.form.get("cover_offset_y") or 0)
    except Exception:
        cover_offset_y = 0.0
    try:
        items = json.loads(request.form.get("items_json") or "[]")
        if not isinstance(items, list):
            items = []
    except Exception:
        return jsonify({"ok": False, "msg": "items_json 不是合法 JSON"}), 400

    # Parse attachment background config
    attachment_bg_config = {}
    try:
        attachment_bg_raw = request.form.get("attachment_bg_config") or "{}"
        attachment_bg_config = json.loads(attachment_bg_raw)
        if not isinstance(attachment_bg_config, dict):
            attachment_bg_config = {}
    except Exception:
        attachment_bg_config = {}

    layouts = _load_layouts()
    layouts[process_code] = {
        "name": layout_name or process_code,
        "base_pdf": base_pdf,
        "use_template": bool(use_template),
        "orientation": "l" if orientation == "l" else "p",
        "cover_source_mode": cover_source_mode,
        "cover_mode": cover_mode,
        "cover_offset_x": cover_offset_x,
        "cover_offset_y": cover_offset_y,
        "items": items,
        "attachment_background_config": attachment_bg_config,
    }
    _save_layouts(layouts)
    return jsonify({"ok": True, "msg": "保存成功"})


@designer_bp.route("/designer/delete", methods=["POST"])
def designer_delete():
    process_code = str(request.form.get("process_code") or "").strip()
    layouts = _load_layouts()
    if process_code in layouts:
        del layouts[process_code]
        _save_layouts(layouts)
    return redirect(url_for("designer_bp.designer_list"))


@designer_bp.route("/designer/preview_print")
def designer_preview_print():
    """
    Print preview entry: generates PDF using designer layout and shows print UI.
    This is called from钉钉打印入口 when designer layout exists.
    """
    process_code = str(request.args.get("process_code") or "").strip()
    instance_id = str(request.args.get("instance_id") or "").strip()
    
    if not process_code or not instance_id:
        return "缺少 process_code 或 instance_id", 400
    
    layouts = _load_layouts()
    layout = layouts.get(process_code)
    if not layout:
        return f"未找到设计器布局: {process_code}", 404
    
    # Call designer preview API directly to generate PDF
    cfg = _cfg()
    ding = _ding()
    
    # Get admin userid from env or use a default
    userid = os.getenv("DINGTALK_ADMIN_USERID") or ""
    
    # Prepare payload for preview API
    payload = {
        "process_code": process_code,
        "instance_id": instance_id,
        "userid": userid,
        "base_pdf": layout.get("base_pdf", ""),
        "use_template": layout.get("use_template", True),
        "orientation": layout.get("orientation", "l"),
        "cover_source_mode": layout.get("cover_source_mode", "base"),
        "cover_mode": layout.get("cover_mode", "strict"),
        "cover_offset_x": layout.get("cover_offset_x", 0),
        "cover_offset_y": layout.get("cover_offset_y", 0),
        "attachment_background_config": layout.get("attachment_background_config", {}),
        "items": layout.get("items", []),
    }
    
    # 如果启用了附件底图，强制 use_template = True
    attachment_bg_config = payload.get("attachment_background_config") or {}
    if attachment_bg_config.get("enabled") and payload.get("cover_source_mode") == "attachment":
        payload["use_template"] = True
        print(f"[DEBUG] 钉钉打印：启用附件底图，强制 use_template = True")
    
    print(f"[DEBUG] designer_preview_print payload:")
    print(f"  - use_template: {payload['use_template']}")
    print(f"  - cover_source_mode: {payload['cover_source_mode']}")
    print(f"  - attachment_bg_config: {payload['attachment_background_config']}")
    
    # Generate PDF using the same logic as designer_preview
    # For now, redirect to a simpler approach: use the existing preview endpoint
    # But we need to render it properly for print view
    
    return render_template(
        "designer_print.html",
        process_code=process_code,
        instance_id=instance_id,
        layout_name=layout.get("name") or process_code,
        layout_json=json.dumps(layout),
    )


@designer_bp.route("/designer/api/render_attachment_bg")
def render_attachment_bg():
    """
    渲染附件底图为 PNG, 用于设计器画布预览
    """
    import fitz
    from io import BytesIO
    
    process_code = request.args.get("process_code", "").strip()
    instance_id = request.args.get("instance_id", "").strip()
    field_id = request.args.get("field_id", "").strip()
    attachment_index = int(request.args.get("attachment_index", "0"))
    page_index = int(request.args.get("page_index", "0"))
    orient = request.args.get("orient", "l").strip()
    
    if not process_code or not instance_id or not field_id:
        return "Missing required parameters", 400
    
    try:
        ding = _ding()
        cfg = _cfg()
        
        # 获取实例数据
        instance = ding.get_process_instance(instance_id)
        if not instance:
            return "Instance not found", 404
        
        # 查找附件字段
        form_values = instance.get("form_component_values") or []
        attachment_field = None
        for comp in form_values:
            if comp.get("id") == field_id:
                attachment_field = comp
                break
        
        if not attachment_field:
            return f"Field {field_id} not found", 404
        
        # 获取附件值
        value = attachment_field.get("value")
        if not value:
            return "No attachment value", 404
        
        # 解析附件 JSON
        try:
            attachments = json.loads(value) if isinstance(value, str) else value
        except Exception:
            return "Invalid attachment format", 400
        
        if not isinstance(attachments, list) or len(attachments) == 0:
            return "No attachments found", 404
        
        if attachment_index >= len(attachments):
            return f"Attachment index {attachment_index} out of range", 404
        
        attachment = attachments[attachment_index]
        
        # 钉钉附件格式：{"fileId": "xxx", "spaceId": "xxx", "fileName": "xxx.pdf", ...}
        # 需要通过 fileId 获取下载 URL
        file_id = str(attachment.get("fileId") or "").strip()
        
        if not file_id:
            return "No fileId in attachment", 404
        
        # 获取下载 URL
        try:
            file_url = ding.get_process_attachment_url(
                process_instance_id=instance_id,
                file_id=file_id
            )
        except Exception as e:
            return f"Failed to get download URL: {str(e)}", 500
        
        # 下载附件
        response = ding.session.get(file_url, timeout=cfg.request_timeout_seconds)
        if response.status_code != 200:
            return f"Failed to download attachment: {response.status_code}", 500
        
        # 打开 PDF
        pdf_bytes = response.content
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        if page_index >= doc.page_count:
            doc.close()
            return f"Page index {page_index} out of range (total {doc.page_count} pages)", 404
        
        # 渲染指定页面为 PNG
        page = doc[page_index]
        
        # 根据方向设置目标尺寸
        target_w, target_h = (842.0, 595.0) if orient == "l" else (595.0, 842.0)
        
        # 计算缩放比例
        scale_x = target_w / page.rect.width
        scale_y = target_h / page.rect.height
        matrix = fitz.Matrix(scale_x, scale_y)
        
        # 渲染为图片
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pix.tobytes("png")
        
        doc.close()
        
        # 返回 PNG
        return send_file(
            BytesIO(png_bytes),
            mimetype="image/png",
            download_name=f"attachment_bg_{instance_id}_{page_index}.png"
        )
        
    except Exception as e:
        return f"Error: {str(e)}", 500
