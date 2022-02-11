from fastapi import APIRouter, Depends

from app.core.facade import BTCWalletService
from app.core.transaction.transaction_interactor import TransactionsResponse
from app.core.wallet.wallet_interactor import (
    AddWalletRequest,
    FetchWalletTransactionsRequest,
    WalletResponse,
)
from app.infrastructure.fastapi.dependables import get_core

wallet_api = APIRouter()


@wallet_api.post("/wallets")
def add_wallet(
    api_key: str, core: BTCWalletService = Depends(get_core)
) -> WalletResponse:
    request = AddWalletRequest(api_key)
    return core.add_wallet(request)


@wallet_api.get("/wallets/{address}")
def get_wallet(
    api_key: str, address: str, core: BTCWalletService = Depends(get_core)
) -> WalletResponse:
    return core.get_wallet(api_key, address)


@wallet_api.get("/wallets/{address}/transactions")
def get_wallet_transactions(
    api_key: str, address: str, core: BTCWalletService = Depends(get_core)
) -> TransactionsResponse:
    request = FetchWalletTransactionsRequest(api_key=api_key, wallet_address=address)
    return core.get_wallet_transactions(request)
