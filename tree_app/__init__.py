from flask import Flask
from flask_smorest import Api


def create_app() -> Flask:
    # create and configure the app
    app = Flask(
        __name__,
        static_url_path="",
        static_folder="templates/static",
        template_folder="templates",
    )

    app.config.from_mapping(
        {
            "API_TITLE": "Tree cache",
            "API_VERSION": "v1",
            "OPENAPI_VERSION": "3.0.2",
            "OPENAPI_URL_PREFIX": "/api",
            "OPENAPI_SWAGGER_UI_PATH": "/doc",
            "OPENAPI_SWAGGER_UI_URL": "https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
        }
    )
    from tree_app.main import bp

    app.register_blueprint(bp)

    from tree_app.api import api_bp

    api = Api(app)
    api.register_blueprint(api_bp, url_prefix="/api")

    return app
