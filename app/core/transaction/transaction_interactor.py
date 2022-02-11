from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.core.repositories import Transaction, UserInfo, Wallet
from app.core.utils import Response, get_btc_to_usd_rate

FEE_PERCENTAGE = 0.015


@dataclass
class TransactionsResponse(Response):
    transactions: Optional[List[Transaction]]


@dataclass
class MakeTransactionRequest:
    api_key: str
    wallet_address_from: str
    wallet_address_to: str
    btc_amount: float


class ITransactionRepository(Protocol):
    def get_user(self, api_key: str) -> Optional[UserInfo]:
        pass

    def get_user_transactions(self, user: UserInfo) -> List[Transaction]:
        pass

    def add_transaction(self, transaction: Transaction) -> None:
        pass

    def get_wallet_user(self, wallet: Wallet) -> UserInfo:
        pass

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
        pass

    def update_wallet_balance(
        self, wallet_address: str, new_btc_balance: float
    ) -> None:
        pass


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
                success=False, message="Invalid credentials", transactions=None
            )

        return TransactionsResponse(
            success=True,
            message="Here are your transactions",
            transactions=self.transaction_repository.get_user_transactions(user),
        )

    def make_transaction(self, request: MakeTransactionRequest) -> Response:
        wallet_from = self.transaction_repository.get_wallet(
            request.wallet_address_from
        )
        wallet_to = self.transaction_repository.get_wallet(request.wallet_address_to)

        if wallet_from is None or wallet_to is None:
            return TransactionsResponse(
                success=False, message="Invalid credentials", transactions=None
            )

        user_from = self.transaction_repository.get_wallet_user(wallet_from)
        user_to = self.transaction_repository.get_wallet_user(wallet_to)
        api_key_user = self.transaction_repository.get_user(request.api_key)
        if api_key_user is None or user_from != api_key_user:
            return TransactionsResponse(
                success=False, message="Invalid credentials", transactions=None
            )

        if wallet_from.btc_balance < request.btc_amount:
            return TransactionsResponse(
                success=False, message="Insufficient funds", transactions=None
            )

        transaction_fee_pct = FEE_PERCENTAGE if user_from != user_to else 0
        exchange_rate = get_btc_to_usd_rate()
        if exchange_rate is None:
            return Response(success=False, message="Could not determine exchange rate")

        transaction = Transaction(
            wallet_from.wallet_address,
            wallet_to.wallet_address,
            request.btc_amount,
            transaction_fee_pct,
            exchange_rate,
        )

        self.transaction_repository.add_transaction(transaction)

        self.transaction_repository.update_wallet_balance(
            wallet_from.wallet_address,
            wallet_from.btc_balance - request.btc_amount,
        )
        self.transaction_repository.update_wallet_balance(
            wallet_to.wallet_address,
            wallet_to.btc_balance + request.btc_amount * (1 - transaction_fee_pct),
        )

        return Response(success=True, message="Transaction successful")
