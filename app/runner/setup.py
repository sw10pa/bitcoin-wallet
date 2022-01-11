from fastapi import FastAPI

from app.core.facade import Service


def setup() -> FastAPI:
    app = FastAPI()
    # app.include_router(receipt_api)
    app.state.core = Service.create()
    return app
