from fastapi import APIRouter, Depends

from app.core.facade import BTCWalletService
from app.core.transaction.transaction_interactor import TransactionsResponse
from app.core.wallet.wallet_interactor import WalletResponse
from app.infrastructure.fastapi.dependables import get_core

wallet_api = APIRouter()


@wallet_api.post("/wallets")
def add_wallet(
    api_key: str, core: BTCWalletService = Depends(get_core)
) -> WalletResponse:
    return core.add_wallet(api_key)


@wallet_api.get("/wallets/{address}")
def get_wallet(
    api_key: str, address: str, core: BTCWalletService = Depends(get_core)
) -> WalletResponse:
    return core.get_wallet(api_key, address)


@wallet_api.get("/wallets/{address}/transactions")
def get_wallet_transactions(
    api_key: str, address: str, core: BTCWalletService = Depends(get_core)
) -> TransactionsResponse:
    return core.get_wallet_transactions(api_key, address)
