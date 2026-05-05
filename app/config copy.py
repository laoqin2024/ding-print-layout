from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import json
from dotenv import load_dotenv


def _env(key: str, default: str | None = None) -> str | None:
    val = os.getenv(key)
    if val is None:
        return default
    val = val.strip()
    return val if val != "" else default


def _project_root() -> Path:
    # app/config.py -> app/ -> project root
    return Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AppConfig:
    # DingTalk
    app_key: str
    app_secret: str
    corp_id: str

    # Flask
    secret_key: str

    # Paths
    base_dir: Path
    pdf_template_dir: Path
    output_dir: Path
    process_config_file: Path
    process_history_file: Path

    # HTTP
    request_timeout_seconds: float = 10.0

    # DingTalk API bases
    oapi_base: str = "https://oapi.dingtalk.com"


class Config:
    """
    Compatibility wrapper for the refactor plan.

    - `Config.load()` provides the typed `AppConfig`.
    - `Config.init_app()` ensures expected directories/files exist.
    """

    @staticmethod
    def load() -> AppConfig:
        return load_config()

    @staticmethod
    def init_app(cfg: AppConfig) -> None:
        cfg.pdf_template_dir.mkdir(parents=True, exist_ok=True)
        cfg.output_dir.mkdir(parents=True, exist_ok=True)
        cfg.process_config_file.parent.mkdir(parents=True, exist_ok=True)
        cfg.process_history_file.parent.mkdir(parents=True, exist_ok=True)

        if not cfg.process_config_file.exists():
            cfg.process_config_file.write_text(json.dumps({}, ensure_ascii=False, indent=4), encoding="utf-8")
        if not cfg.process_history_file.exists():
            cfg.process_history_file.write_text(json.dumps([], ensure_ascii=False, indent=4), encoding="utf-8")

    @staticmethod
    def validate_security(cfg: AppConfig) -> None:
        missing = []
        if not cfg.app_key:
            missing.append("DINGTALK_APP_KEY")
        if not cfg.app_secret:
            missing.append("DINGTALK_APP_SECRET")
        if not cfg.corp_id:
            missing.append("DINGTALK_CORP_ID")
        if not cfg.secret_key:
            missing.append("FLASK_SECRET_KEY")

        if missing:
            keys = ", ".join(missing)
            raise RuntimeError(f"Missing required environment variables: {keys}")


def load_config() -> AppConfig:
    """
    Centralized config loader.

    Notes:
    - Secrets should come from environment variables in production.
    - Defaults keep current behavior to avoid breaking existing deployment.
    """
    base_dir = _project_root()
    # Auto-load local .env so users don't need manual `export`.
    # Existing shell env variables still take precedence by default.
    load_dotenv(base_dir / ".env", override=False)

    # Security first: no real secret defaults in source code.
    app_key = _env("DINGTALK_APP_KEY", "") or ""
    app_secret = _env("DINGTALK_APP_SECRET", "") or ""
    corp_id = _env("DINGTALK_CORP_ID", "") or ""
    secret_key = _env("FLASK_SECRET_KEY", "") or ""

    # New, clearer default locations (can be overridden via env)
    pdf_template_dir = Path(_env("PDF_TEMPLATE_DIR", str(base_dir / "templates" / "pdf_templates")) or (base_dir / "templates" / "pdf_templates"))
    output_dir = Path(_env("OUTPUT_DIR", str(base_dir / "static" / "outputs")) or (base_dir / "static" / "outputs"))
    process_config_file = Path(
        _env("PROCESS_CONFIG_FILE", str(base_dir / "data" / "process_configs.json"))
        or (base_dir / "data" / "process_configs.json")
    )
    process_history_file = Path(
        _env("PROCESS_HISTORY_FILE", str(base_dir / "data" / "process_configs.history.json"))
        or (base_dir / "data" / "process_configs.history.json")
    )

    return AppConfig(
        app_key=app_key,
        app_secret=app_secret,
        corp_id=corp_id,
        secret_key=secret_key,
        base_dir=base_dir,
        pdf_template_dir=pdf_template_dir,
        output_dir=output_dir,
        process_config_file=process_config_file,
        process_history_file=process_history_file,
        request_timeout_seconds=float(_env("REQUEST_TIMEOUT_SECONDS", "10") or "10"),
        oapi_base=_env("DINGTALK_OAPI_BASE", "https://oapi.dingtalk.com") or "https://oapi.dingtalk.com",
    )

