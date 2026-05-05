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


def _resolve_path(env_key: str, default_path: Path) -> Path:
    """
    安全路径解析：
    如果环境变量提供的路径是不可写的绝对路径（如服务器残留的 /root），
    则强制回退到本地项目根目录下的默认路径。
    """
    env_val = _env(env_key)
    if not env_val:
        return default_path
    
    path = Path(env_val)
    # 检查路径是否是以 /root 或其他在 Mac 上无权访问的系统绝对路径开头
    # 如果路径是绝对路径且不可写，或者包含明显的 Linux 服务器特征
    if path.is_absolute():
        if str(path).startswith('/root') or str(path).startswith('/home'):
            print(f"检测到服务器残留路径 {env_val}，已自动重定向到本地项目目录。")
            return default_path
    return path


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
    process_history_file: Path

    # HTTP
    request_timeout_seconds: float = 10.0

    # DingTalk API bases
    oapi_base: str = "https://oapi.dingtalk.com"


class Config:
    """
    Compatibility wrapper for the refactor plan.
    """

    @staticmethod
    def load() -> AppConfig:
        return load_config()

    @staticmethod
    def init_app(cfg: AppConfig) -> None:
        # 确保所有父级目录存在
        try:
            cfg.pdf_template_dir.mkdir(parents=True, exist_ok=True)
            cfg.output_dir.mkdir(parents=True, exist_ok=True)
            cfg.process_history_file.parent.mkdir(parents=True, exist_ok=True)

            if not cfg.process_history_file.exists():
                cfg.process_history_file.write_text(json.dumps([], ensure_ascii=False, indent=4), encoding="utf-8")
        except PermissionError:
            print("权限错误：无法创建目录。请检查 config.py 中的路径配置或 .env 文件。")
            raise

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
    base_dir = _project_root()
    
    # 加载 .env
    env_path = base_dir / ".env"
    load_dotenv(env_path, override=False)

    # 基础安全配置
    app_key = _env("DINGTALK_APP_KEY", "") or ""
    app_secret = _env("DINGTALK_APP_SECRET", "") or ""
    corp_id = _env("DINGTALK_CORP_ID", "") or ""
    secret_key = _env("FLASK_SECRET_KEY", "") or ""

    # 使用安全解析函数处理路径，防止服务器硬编码路径干扰
    pdf_template_dir = _resolve_path("PDF_TEMPLATE_DIR", base_dir / "templates" / "pdf_templates")
    output_dir = _resolve_path("OUTPUT_DIR", base_dir / "static" / "outputs")
    process_history_file = _resolve_path("PROCESS_HISTORY_FILE", base_dir / "data" / "process_versions.json")

    return AppConfig(
        app_key=app_key,
        app_secret=app_secret,
        corp_id=corp_id,
        secret_key=secret_key,
        base_dir=base_dir,
        pdf_template_dir=pdf_template_dir,
        output_dir=output_dir,
        process_history_file=process_history_file,
        request_timeout_seconds=float(_env("REQUEST_TIMEOUT_SECONDS", "10") or "10"),
        oapi_base=_env("DINGTALK_OAPI_BASE", "https://oapi.dingtalk.com") or "https://oapi.dingtalk.com",
    )