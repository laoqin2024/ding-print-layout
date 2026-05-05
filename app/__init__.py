from __future__ import annotations

import os
from flask import Flask

from app.config import Config
from app.services.dingtalk_service import DingTalkService


def create_app() -> Flask:
    cfg = Config.load()
    Config.validate_security(cfg)
    Config.init_app(cfg)

    app = Flask(
        __name__,
        template_folder=str(cfg.base_dir / "templates"),
        static_folder=str(cfg.base_dir / "static"),
    )
    app.secret_key = cfg.secret_key

    # Shared objects
    app.extensions["app_cfg"] = cfg
    app.extensions["dingtalk"] = DingTalkService(cfg)

    # Blueprints
    from app.routes.portal import portal_bp
    from app.routes.printing import print_bp
    from app.routes.admin import admin_bp
    from app.routes.designer import designer_bp
    from app.routes.users import users_bp

    app.register_blueprint(portal_bp)
    app.register_blueprint(print_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(designer_bp)
    app.register_blueprint(users_bp)

    @app.context_processor
    def inject_asset_version():
        dist_css = cfg.base_dir / "static" / "dist" / "app.css"
        legacy_core = cfg.base_dir / "static" / "dist-legacy" / "core.js"
        try:
            m1 = int(os.path.getmtime(dist_css))
            m2 = int(os.path.getmtime(legacy_core)) if legacy_core.exists() else m1
            asset_v = str(max(m1, m2))
        except OSError:
            asset_v = "1"
        return {"asset_v": asset_v}

    return app

