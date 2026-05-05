from __future__ import annotations

import os
import json

from flask import Blueprint, current_app, redirect, render_template, request, url_for

from app.services.dingtalk_service import DingTalkError, DingTalkService
from app.services.pdf_service import PdfServiceError, generate_print_pdf, load_process_configs, load_process_node_configs


print_bp = Blueprint("print_bp", __name__)


def _cfg():
    return current_app.extensions["app_cfg"]


def _ding() -> DingTalkService:
    return current_app.extensions["dingtalk"]


def _load_designer_layouts() -> dict:
    """Load designer layouts from print_layouts.json"""
    cfg = _cfg()
    path = cfg.base_dir / "data" / "print_layouts.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


@print_bp.route("/open_approval")
def open_approval():
    """
    Stable scan entry:
    QR -> this route -> latest DingTalk task URL.
    """
    instance_id = str(request.args.get("id") or "").strip()
    if not instance_id:
        return "缺少实例ID", 400
    try:
        instance = _ding().get_process_instance(instance_id)
    except DingTalkError as exc:
        return f"读取实例失败: {exc}", 400
    tasks = (instance or {}).get("tasks") or []
    task = tasks[0] if isinstance(tasks, list) and tasks and isinstance(tasks[0], dict) else {}
    target = str(task.get("url") or "").strip()
    if target and not target.startswith("http://") and not target.startswith("https://"):
        if target.startswith("aflow.dingtalk.com?"):
            target = "https://aflow.dingtalk.com/?" + target.split("?", 1)[1]
        else:
            target = f"https://{target}"
    if not target:
        # Fallback to aflow short-entry style URL.
        target = f"https://aflow.dingtalk.com/qr/{instance_id}"
    return redirect(target, code=302)


@print_bp.route("/print_view")
def print_view():
    instance_id = request.args.get("id") or ""
    passed_p_code = request.args.get("p_code")  # hard requirement: support URL fallback

    ding = _ding()
    try:
        instance = ding.get_process_instance(instance_id)
    except DingTalkError:
        return "单据详情获取失败", 500

    # hard requirement: URL param fallback when DingTalk returns empty process_code
    p_code = DingTalkService.normalize_code(passed_p_code or instance.get("process_code") or "")

    # Priority 1: Check if designer layout exists
    designer_layouts = _load_designer_layouts()
    designer_layout = designer_layouts.get(p_code)
    
    # Debug logging
    print(f"[DEBUG] print_view called:")
    print(f"  - instance_id: {instance_id}")
    print(f"  - passed_p_code: {passed_p_code}")
    print(f"  - normalized p_code: {p_code}")
    print(f"  - designer_layouts keys: {list(designer_layouts.keys())}")
    print(f"  - designer_layout found: {designer_layout is not None}")
    
    if designer_layout:
        # Use new designer-based printing
        # Redirect to designer preview with print mode
        print(f"[DEBUG] Redirecting to designer preview")
        from flask import url_for
        return redirect(url_for('designer_bp.designer_preview_print', 
                               process_code=p_code, 
                               instance_id=instance_id), code=302)
    
    print(f"[DEBUG] Using legacy printing system")
    
    # Priority 2: Fallback to old printing system (套印模块)
    cfg = _cfg()
    configs = load_process_configs(cfg)
    node_configs = load_process_node_configs(cfg)
    p_config = configs.get(p_code)
    if not p_config:
        return f"未找到流程配置（设计器布局或套印配置）: {p_code}", 404

    # Prefer printing from the process PDF attachment (if present),
    # fallback to static template when attachment cannot be downloaded.
    source_pdf_bytes = ding.download_process_attachment_pdf(process_instance_id=instance_id, instance=instance)

    try:
        out_path, _sigs, report = generate_print_pdf(
            cfg=cfg,
            process_config=p_config,
            instance_id=instance_id,
            instance=instance,
            approval_no=str(instance.get("business_id") or instance_id),
            node_config=node_configs.get(p_code) if isinstance(node_configs, dict) else None,
            http_session=ding.session,
            source_pdf_bytes=source_pdf_bytes,
        )
    except (PdfServiceError, Exception) as e:
        return f"PDF合成失败: {str(e)}", 500

    out_name = out_path.name
    pdf_url = url_for("static", filename=f"outputs/{out_name}")
    try:
        pdf_bytes = int(os.path.getsize(out_path))
    except OSError:
        pdf_bytes = 0
    try:
        pdf_v = str(int(os.path.getmtime(out_path)))
    except OSError:
        pdf_v = "1"
    pdf_url = f"{pdf_url}?v={pdf_v}"
    
    # 生成 JSAPI 配置（用于钉钉打印功能）
    jsapi_config = None
    try:
        jsapi_config = ding.get_jsapi_config(request.url)
    except Exception as e:
        print(f"[WARN] Failed to generate jsapi_config: {e}")
    
    return render_template(
        "print.html",
        pdf_url=pdf_url,
        pdf_name=out_name,
        pdf_bytes=pdf_bytes,
        pdf_v=pdf_v,
        instance_id=instance_id,
        process_name=p_config.get("name") or "",
        check_report=report,
        jsapi_config=jsapi_config,
        using_legacy=True,
    )

