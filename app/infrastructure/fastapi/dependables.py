from starlette.requests import Request

from app.core.facade import BTCWalletService


def get_core(request: Request) -> BTCWalletService:
    core: BTCWalletService = request.app.state.core
    return core
