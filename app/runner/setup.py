from fastapi import FastAPI

from app.core.facade import BTCWalletService
from app.infrastructure.fastapi.admin import admin_api
from app.infrastructure.fastapi.transaction import transaction_api
from app.infrastructure.fastapi.user import user_api
from app.infrastructure.fastapi.wallet import wallet_api
from app.infrastructure.sqlite.sqlite_repository import SQLiteRepository


def setup() -> FastAPI:
    app = FastAPI()
    app.include_router(admin_api)
    app.include_router(transaction_api)
    app.include_router(user_api)
    app.include_router(wallet_api)
    repository = SQLiteRepository()
    app.state.core = BTCWalletService.create(
        repository, repository, repository, repository
    )
    return app
