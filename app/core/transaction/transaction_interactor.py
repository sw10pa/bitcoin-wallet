from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.core.entities import Response, Transaction
from app.core.transaction.transaction_CoR import (
    BalanceCheckHandler,
    ExchangeRateHandler,
    MakeTransactionArgs,
    MakeTransactionHandler,
    MakeTransactionRequest,
    UserCheckHandler,
    WalletCheckHandler,
)
from app.core.transaction.transaction_repository import ITransactionRepository


@dataclass
class TransactionsResponse(Response):
    transactions: Optional[List[Transaction]]


class ITransactionInteractor(Protocol):
    def get_user_transactions(self, api_key: str) -> TransactionsResponse:
        pass

    def make_transaction(self, request: MakeTransactionRequest) -> Response:
        pass


class TransactionInteractor:
    def __init__(
        self,
        transaction_repository: ITransactionRepository,
    ):
        self.transaction_repository = transaction_repository

    def get_user_transactions(self, api_key: str) -> TransactionsResponse:
        user = self.transaction_repository.get_user(api_key)
        if user is None:
            return TransactionsResponse(
                success=False,
                message="Invalid credentials",
                status_code=401,
                transactions=None,
            )

        return TransactionsResponse(
            success=True,
            message="Here are your transactions",
            status_code=200,
            transactions=self.transaction_repository.get_user_transactions(user),
        )

    def make_transaction(self, request: MakeTransactionRequest) -> Response:
        handler = WalletCheckHandler()
        handler.set_next(UserCheckHandler()).set_next(BalanceCheckHandler()).set_next(
            ExchangeRateHandler()
        ).set_next(MakeTransactionHandler())

        args = MakeTransactionArgs(
            repository=self.transaction_repository, request=request
        )
        return handler.handle(args)
