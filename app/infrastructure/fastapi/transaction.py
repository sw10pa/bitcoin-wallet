from fastapi import APIRouter, Depends

from app.core.facade import BTCWalletService
from app.core.transaction.transaction_CoR import MakeTransactionRequest
from app.core.transaction.transaction_interactor import TransactionsResponse
from app.core.utils import Response
from app.infrastructure.fastapi.dependables import get_core

transaction_api = APIRouter()


@transaction_api.get("/transactions")
def get_transactions(
    api_key: str, core: BTCWalletService = Depends(get_core)
) -> TransactionsResponse:
    return core.get_transactions(api_key)


@transaction_api.post("/transactions")
def make_transaction(
    api_key: str,
    wallet_address_from: str,
    wallet_address_to: str,
    btc_amount: float,
    core: BTCWalletService = Depends(get_core),
) -> Response:
    request = MakeTransactionRequest(
        api_key, wallet_address_from, wallet_address_to, btc_amount
    )
    return core.make_transaction(request)
