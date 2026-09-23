"""Webhook entry point: python -m atlas_ultimate_crm.webhook"""
import uvicorn


def main():
    from atlas_ultimate_crm.bootstrap import Bootstrap
    bootstrap = Bootstrap()
    bootstrap.initialize()

    from atlas_ultimate_crm.webhook.app import create_app
    app = create_app(bootstrap)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
