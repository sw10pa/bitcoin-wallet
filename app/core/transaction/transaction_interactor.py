from dataclasses import dataclass
from typing import List, Protocol

from app.core.facade import Response
from app.core.repositories import IFatherRepository, Transaction

FEE_PERCENTAGE = 0.015


@dataclass
class TransactionsResponse(Response):
    transactions: List[Transaction]


@dataclass
class MakeTransactionRequest:
    api_key: str
    wallet_address_from: str
    wallet_address_to: str
    btc_amount: float


class ITransactionInteractor(Protocol):
    def get_user_transactions(self, api_key: str) -> TransactionsResponse:
        pass

    def make_transaction(self, request: MakeTransactionRequest) -> Response:
        pass


class TransactionInteractor:
    def __init__(
        self,
        transaction_repository: IFatherRepository,
        wallet_repository: IFatherRepository,
    ):  # TODO change to ITransactionRepository, IWalletRepository
        self.transaction_repository = transaction_repository
        self.wallet_repository = wallet_repository

    def get_user_transactions(self, api_key: str) -> TransactionsResponse:
        transactions = self.transaction_repository.get_user_transactions(api_key)
        # TODO
        return TransactionsResponse(
            success=True, message="TODO", transactions=transactions
        )

    def make_transaction(self, request: MakeTransactionRequest) -> Response:

        user_from = self.wallet_repository.get_wallet_user(request.wallet_address_from)
        # TODO if user_from.api_key != request.api_key: ERROR
        wallet_from = self.wallet_repository.get_wallet(request.wallet_address_from)
        # TODO check if wallet is valid

        user_to = self.wallet_repository.get_wallet_user(request.wallet_address_to)
        wallet_to = self.wallet_repository.get_wallet(request.wallet_address_to)

        transaction_fee_pct = FEE_PERCENTAGE
        # TODO if users not equal take fee
        exchange_rate = 1.7
        # TODO convert to BTC

        transaction = Transaction(
            wallet_from.wallet_address,
            wallet_to.wallet_address,
            request.btc_amount,
            transaction_fee_pct,
            exchange_rate,
        )

        self.transaction_repository.add_transaction(transaction)

        self.wallet_repository.update_wallet_balance(
            wallet_from.wallet_address, wallet_from.btc_balance - request.btc_amount
        )
        self.wallet_repository.update_wallet_balance(
            wallet_to.wallet_address, wallet_to.btc_balance + request.btc_amount
        )
        # TODO check if wallet_address_from is valid

        return Response(success=True, message="TODO")
