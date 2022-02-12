from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.core.repositories import Transaction, UserInfo, Wallet
from app.core.transaction.transaction_repository import ITransactionRepository
from app.core.utils import Response, get_btc_to_usd_rate

FEE_PERCENTAGE = 0.015


@dataclass
class MakeTransactionRequest:
    api_key: str
    wallet_address_from: str
    wallet_address_to: str
    btc_amount: float


@dataclass
class MakeTransactionArgs:
    repository: ITransactionRepository
    request: MakeTransactionRequest
    wallet_from: Optional[Wallet] = None
    wallet_to: Optional[Wallet] = None
    user_from: Optional[UserInfo] = None
    user_to: Optional[UserInfo] = None
    exchange_rate: Optional[float] = None


class ITransactionHandler(ABC):
    @abstractmethod
    def set_next(self, handler: "ITransactionHandler") -> "ITransactionHandler":
        pass

    @abstractmethod
    def handle(self, args: MakeTransactionArgs) -> Response:
        pass


class TransactionHandler(ITransactionHandler):

    _next_handler: Optional[ITransactionHandler] = None

    def set_next(self, handler: ITransactionHandler) -> ITransactionHandler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, args: MakeTransactionArgs) -> Response:
        if self._next_handler:
            return self._next_handler.handle(args)

        return Response(success=True, message="Transaction successful")


class WalletCheckHandler(TransactionHandler):
    def handle(self, args: MakeTransactionArgs) -> Response:
        wallet_from = args.repository.get_wallet(args.request.wallet_address_from)
        wallet_to = args.repository.get_wallet(args.request.wallet_address_to)

        if wallet_from is None or wallet_to is None:
            return Response(
                success=False,
                message="Invalid credentials",
            )
        args.wallet_from = wallet_from
        args.wallet_to = wallet_to
        return super().handle(args)


class UserCheckHandler(TransactionHandler):
    def handle(self, args: MakeTransactionArgs) -> Response:
        assert args.wallet_from is not None
        assert args.wallet_to is not None
        user_from = args.repository.get_wallet_user(args.wallet_from)
        user_to = args.repository.get_wallet_user(args.wallet_to)
        api_key_user = args.repository.get_user(args.request.api_key)
        if api_key_user is None or user_from != api_key_user:
            return Response(
                success=False,
                message="Invalid credentials",
            )
        args.user_from = user_from
        args.user_to = user_to
        return super().handle(args)


class BalanceCheckHandler(TransactionHandler):
    def handle(self, args: MakeTransactionArgs) -> Response:
        assert args.wallet_from is not None
        if args.wallet_from.btc_balance < args.request.btc_amount:
            return Response(
                success=False,
                message="Insufficient funds",
            )
        return super().handle(args)


class ExchangeRateHandler(TransactionHandler):
    def handle(self, args: MakeTransactionArgs) -> Response:
        exchange_rate = get_btc_to_usd_rate()
        if exchange_rate is None:
            return Response(success=False, message="Could not determine exchange rate")
        args.exchange_rate = exchange_rate
        return super().handle(args)


class MakeTransactionHandler(TransactionHandler):
    def handle(self, args: MakeTransactionArgs) -> Response:
        transaction_fee_pct = FEE_PERCENTAGE if args.user_from != args.user_to else 0

        assert args.wallet_from is not None
        assert args.wallet_to is not None
        assert args.exchange_rate is not None

        transaction = Transaction(
            args.wallet_from.wallet_address,
            args.wallet_to.wallet_address,
            args.request.btc_amount,
            transaction_fee_pct,
            args.exchange_rate,
        )

        args.repository.add_transaction(transaction)

        args.repository.update_wallet_balance(
            args.wallet_from.wallet_address,
            args.wallet_from.btc_balance - args.request.btc_amount,
        )
        args.repository.update_wallet_balance(
            args.wallet_to.wallet_address,
            args.wallet_to.btc_balance
            + args.request.btc_amount * (1 - transaction_fee_pct),
        )
        return super().handle(args)
