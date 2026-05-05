from __future__ import annotations

import json
import os
import re
from io import BytesIO
from pathlib import Path

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, send_file, url_for

from app.services.dingtalk_service import DingTalkError, DingTalkService
from app.services.pdf_service import (
    append_process_version,
    list_pdf_templates,
    list_process_versions,
    load_process_configs,
    render_pdf_page_png,
    rollback_process_version,
    save_process_configs,
)


admin_bp = Blueprint("admin_bp", __name__)


def _cfg():
    return current_app.extensions["app_cfg"]


def _ding() -> DingTalkService:
    return current_app.extensions["dingtalk"]


def _node_cfg_path(cfg) -> Path:
    custom = (os.getenv("PROCESS_NODE_CONFIG_FILE") or "").strip()
    return Path(custom) if custom else (cfg.base_dir / "data" / "process_node_configs.json")


def _load_node_cfg(cfg) -> dict:
    path = _node_cfg_path(cfg)
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_node_cfg(cfg, data: dict) -> None:
    path = _node_cfg_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data or {}, ensure_ascii=False, indent=2), encoding="utf-8")


def _run_health_checks():
    cfg = _cfg()
    ding = _ding()
    config = load_process_configs(cfg)
    first_code = next(iter(config.keys()), "")
    first_item = config.get(first_code) if first_code else None
    userid = (os.getenv("DINGTALK_ADMIN_USERID") or "").strip()

    checks = []

    # 1) DingTalk process list connectivity
    try:
        process_count = len(ding.list_processes_by_userid(offset=0, size=20))
        checks.append({"key": "process_api", "ok": True, "msg": f"流程接口正常，返回 {process_count} 条"})
    except Exception as exc:
        checks.append({"key": "process_api", "ok": False, "msg": f"流程接口异常: {exc}"})

    # 2) Process instances query by configured process_code + admin userid
    if not first_code:
        checks.append({"key": "instances_api", "ok": False, "msg": "未找到任何流程配置，无法测试实例接口"})
    elif not userid:
        checks.append({"key": "instances_api", "ok": False, "msg": "缺少 DINGTALK_ADMIN_USERID，无法测试实例接口"})
    else:
        try:
            ids = ding.list_process_instance_ids(first_code, userid, size=3)
            checks.append({"key": "instances_api", "ok": True, "msg": f"实例接口正常，返回 {len(ids)} 条"})
        except Exception as exc:
            checks.append({"key": "instances_api", "ok": False, "msg": f"实例接口异常: {exc}"})

    # 3) PDF template file existence
    if not first_item or not first_item.get("base_pdf"):
        checks.append({"key": "pdf_template", "ok": False, "msg": "流程配置缺少 base_pdf，无法检查模板文件"})
    else:
        pdf_name = first_item.get("base_pdf")
        pdf_path = cfg.pdf_template_dir / pdf_name
        if pdf_path.exists():
            checks.append({"key": "pdf_template", "ok": True, "msg": f"模板文件存在: {pdf_name}"})
        else:
            checks.append({"key": "pdf_template", "ok": False, "msg": f"模板文件不存在: {pdf_name}"})

    # 4) PDF render health
    if not first_item or not first_item.get("base_pdf"):
        checks.append({"key": "pdf_render", "ok": False, "msg": "缺少可测试的 PDF 配置，无法渲染检查"})
    else:
        try:
            orient = first_item.get("orientation", "p")
            png_bytes = render_pdf_page_png(cfg, first_item.get("base_pdf"), 0, orient)
            checks.append({"key": "pdf_render", "ok": len(png_bytes) > 0, "msg": f"PDF 渲染正常，PNG {len(png_bytes)} bytes"})
        except Exception as exc:
            checks.append({"key": "pdf_render", "ok": False, "msg": f"PDF 渲染异常: {exc}"})

    summary_ok = all(item.get("ok") for item in checks)
    return {
        "ok": summary_ok,
        "checks": checks,
        "meta": {
            "process_code": first_code,
            "admin_userid": userid or "(未配置)",
        },
    }


@admin_bp.route("/admin")
def admin_list():
    cfg = _cfg()
    config = load_process_configs(cfg)
    return render_template("admin_list.html", config=config)


@admin_bp.route("/admin/delete/<path:code>")
def admin_delete(code: str):
    cfg = _cfg()
    config = load_process_configs(cfg)
    target_code = DingTalkService.normalize_code(code)
    if target_code in config:
        previous = config.get(target_code)
        del config[target_code]
        save_process_configs(cfg, config)
        append_process_version(
            cfg=cfg,
            process_code=target_code,
            action="delete",
            previous=previous,
            current=None,
            operator=request.remote_addr or "admin",
        )
        flash(f"已删除流程: {target_code}")
    return redirect(url_for("admin_bp.admin_list"))


@admin_bp.route("/admin/edit")
def admin_edit():
    """旧的编辑页面，已废弃，重定向到设计器"""
    p_code = request.args.get("code", "")
    if p_code:
        # 如果有 code 参数，重定向到设计器并加载该模板
        return redirect(url_for("designer_bp.designer_edit", load_code=p_code))
    else:
        # 如果没有 code，重定向到设计器首页
        return redirect(url_for("designer_bp.designer_list"))


@admin_bp.route("/admin/node_edit")
def admin_node_edit():
    """旧的节点编辑页面，已废弃，重定向到设计器"""
    p_code = request.args.get("code", "")
    if p_code:
        return redirect(url_for("designer_bp.designer_edit", load_code=p_code))
    else:
        return redirect(url_for("designer_bp.designer_list"))


@admin_bp.route("/admin/node_save", methods=["POST"])
def admin_node_save():
    """旧的节点保存接口，已废弃，重定向到设计器"""
    flash("此功能已迁移到排版设计器，请使用设计器进行编辑")
    return redirect(url_for("designer_bp.designer_list"))


@admin_bp.route("/admin/save", methods=["POST"])
def admin_save():
    """旧的保存接口，已废弃，重定向到设计器"""
    flash("此功能已迁移到排版设计器，请使用设计器进行编辑")
    return redirect(url_for("designer_bp.designer_list"))
    p_code = DingTalkService.normalize_code(request.form.get("process_code"))
    previous = config.get(p_code)
    current = {
        "name": request.form.get("name"),
        "base_pdf": request.form.get("base_pdf"),
        "orientation": request.form.get("orientation", "p"),
        "zones": json.loads(request.form.get("zones_json") or "[]"),
    }
    config[p_code] = current
    save_process_configs(cfg, config)
    append_process_version(
        cfg=cfg,
        process_code=p_code,
        action="save",
        previous=previous,
        current=current,
        operator=request.remote_addr or "admin",
        reason=request.form.get("version_reason", ""),
    )
    flash("保存成功")
    return redirect(url_for("admin_bp.admin_list"))


@admin_bp.route("/admin/versions")
def admin_versions():
    cfg = _cfg()
    p_code = DingTalkService.normalize_code(request.args.get("code", ""))
    return jsonify({"versions": list_process_versions(cfg, p_code, limit=30)})


@admin_bp.route("/admin/rollback", methods=["POST"])
def admin_rollback():
    cfg = _cfg()
    p_code = DingTalkService.normalize_code(request.form.get("process_code", ""))
    version_id = (request.form.get("version_id") or "").strip()
    if not p_code or not version_id:
        return jsonify({"ok": False, "msg": "参数不完整"}), 400
    result = rollback_process_version(cfg, p_code, version_id, operator=request.remote_addr or "admin")
    return jsonify(result), (200 if result.get("ok") else 400)


@admin_bp.route("/admin/search_processes")
def search_processes():
    q = (request.args.get("q", "") or "").lower()
    ding = _ding()
    try:
        procs, _capped, _backend = ding.list_all_approval_templates(page_size=100, max_pages=500)
        results = []
        for p in procs:
            if not isinstance(p, dict):
                continue
            pid = DingTalkService.normalize_code(p.get("process_code") or p.get("processCode") or "")
            if not pid:
                continue
            text = str(p.get("name") or p.get("process_name") or pid)
            if q and q not in text.lower() and q not in pid.lower():
                continue
            results.append({"id": pid, "text": text})
        return jsonify({"results": results})
    except (DingTalkError, Exception):
        return jsonify({"results": []})


@admin_bp.route("/admin/process_instances")
def process_instances():
    """
    Query recent process instances by process_code.
    Query:
      - process_code (required)
      - userid (optional, fallback to env DINGTALK_ADMIN_USERID)
    """
    process_code = DingTalkService.normalize_code(request.args.get("process_code", ""))
    userid = (request.args.get("userid") or os.getenv("DINGTALK_ADMIN_USERID") or "").strip()
    size = int(request.args.get("size", 20) or 20)
    size = max(1, min(size, 50))

    if not process_code:
        return jsonify({"ok": False, "msg": "缺少 process_code", "instances": []}), 400
    if not userid:
        return jsonify(
            {
                "ok": False,
                "msg": "缺少 userid，请传参 userid 或配置 DINGTALK_ADMIN_USERID",
                "instances": [],
            }
        ), 400

    ding = _ding()
    try:
        ins_ids = ding.list_process_instance_ids(process_code, userid, size=size)
    except (DingTalkError, Exception):
        return jsonify({"ok": False, "msg": "读取审批实例失败", "instances": []}), 400

    out = []
    for ins_id in ins_ids:
        try:
            ins = ding.get_process_instance(ins_id)
        except (DingTalkError, Exception):
            continue
        out.append(
            {
                "id": ins_id,
                "title": ins.get("title") or "",
                "create_time": ins.get("create_time") or 0,
                "status": ins.get("status") or "",
                "result": ins.get("result") or "",
            }
        )

    return jsonify({"ok": True, "instances": out})


@admin_bp.route("/admin/userid_by_authcode")
def admin_userid_by_authcode():
    auth_code = (request.args.get("code") or "").strip()
    if not auth_code:
        return jsonify({"ok": False, "msg": "缺少 code", "userid": ""}), 400
    ding = _ding()
    try:
        userid = ding.get_userid_by_auth_code(auth_code)
    except (DingTalkError, Exception):
        return jsonify({"ok": False, "msg": "获取 userid 失败", "userid": ""}), 400
    return jsonify({"ok": True, "userid": userid})


@admin_bp.route("/admin/signature_components")
def signature_components():
    """
    Read signature-like form components from a specific process instance.
    Query:
      - instance_id: DingTalk process instance id
    """
    instance_id = (request.args.get("instance_id") or "").strip()
    if not instance_id:
        return jsonify({"ok": False, "msg": "缺少 instance_id", "components": []}), 400

    ding = _ding()
    try:
        instance = ding.get_process_instance(instance_id)
    except (DingTalkError, Exception):
        return jsonify({"ok": False, "msg": "审批实例读取失败", "components": []}), 400

    components = []
    for c in (instance or {}).get("form_component_values", []) or []:
        ctype = c.get("component_type")
        if ctype not in ["SignatureField", "DDAttachment"]:
            continue
        components.append(
            {
                "id": str(c.get("id") or ""),
                "name": str(c.get("name") or ""),
                "component_type": str(ctype or ""),
            }
        )

    return jsonify({"ok": True, "components": components})


@admin_bp.route("/admin/instance_tasks")
def instance_tasks():
    """
    Read DingTalk process instance tasks and return node-level info.

    Query:
      - instance_id: DingTalk process instance id (required)
    """
    instance_id = (request.args.get("instance_id") or "").strip()
    if not instance_id:
        return jsonify({"ok": False, "msg": "缺少 instance_id", "tasks": []}), 400

    ding = _ding()
    try:
        instance = ding.get_process_instance(instance_id)
    except (DingTalkError, Exception):
        return jsonify({"ok": False, "msg": "审批实例读取失败", "tasks": []}), 400

    tasks = (instance or {}).get("tasks", []) or []
    out = []
    for t in tasks:
        out.append(
            {
                "activity_id": str(t.get("activity_id") or "").strip(),
                "taskid": str(t.get("taskid") or "").strip(),
                "userid": str(t.get("userid") or "").strip(),
                "task_status": str(t.get("task_status") or "").strip(),
                "task_result": str(t.get("task_result") or "").strip(),
                "create_time": t.get("create_time") or "",
                "finish_time": t.get("finish_time") or "",
            }
        )

    return jsonify({"ok": True, "tasks": out})


@admin_bp.route("/admin/health")
def admin_health_page():
    result = _run_health_checks()
    return render_template("admin_health.html", result=result)


@admin_bp.route("/admin/health/check")
def admin_health_check():
    return jsonify(_run_health_checks())


@admin_bp.route("/admin/pdf_render/<path:filename>")
def pdf_render(filename: str):
    cfg = _cfg()
    try:
        page_num = int(request.args.get("page", 0))
        orient = request.args.get("orient", "p")
        png_bytes = render_pdf_page_png(cfg, filename, page_num, orient)
        return send_file(BytesIO(png_bytes), mimetype="image/png")
    except Exception:
        return "Render Error", 500


@admin_bp.route("/admin/upload", methods=["POST"])
def upload_file():
    cfg = _cfg()
    file = request.files.get("file")
    if file:
        safe_name = re.sub(r'[\\/:*?"<>|]', "_", file.filename)
        (cfg.pdf_template_dir).mkdir(parents=True, exist_ok=True)
        file.save(str(cfg.pdf_template_dir / safe_name))
    return redirect(url_for("admin_bp.admin_list"))

