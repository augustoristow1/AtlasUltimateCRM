from fastapi import FastAPI
from atlas_ultimate_crm.webhook.routes import create_router


def create_app(bootstrap) -> FastAPI:
    app = FastAPI(title="Atlas Ultimate CRM Webhook", version="0.1.0")
    router = create_router(bootstrap)
    app.include_router(router)
    return app
