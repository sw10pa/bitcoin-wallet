import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.core.entities import Response, UserInfo, Wallet
from app.core.utils import get_btc_to_usd_rate
from app.core.wallet.wallet_repository import IWalletRepository

MAX_WALLET_COUNT = 3
DEFAULT_INITIAL_BALANCE = 1.0


@dataclass
class WalletHandlerArgs:
    repository: IWalletRepository
    api_key: str
    wallet_address: Optional[str] = None
    user: Optional[UserInfo] = None
    exchange_rate: Optional[float] = None
    wallet: Optional[Wallet] = None


class IWalletHandler(ABC):
    @abstractmethod
    def set_next(self, handler: "IWalletHandler") -> "IWalletHandler":
        pass

    @abstractmethod
    def handle(self, args: WalletHandlerArgs) -> Response:
        pass


class WalletHandler(IWalletHandler):
    _next_handler: Optional[IWalletHandler] = None

    def set_next(self, handler: IWalletHandler) -> IWalletHandler:
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, args: WalletHandlerArgs) -> Response:
        if self._next_handler:
            return self._next_handler.handle(args)

        return Response(success=True, message="OK", status_code=200)


class UserCheckHandler(WalletHandler):
    def handle(self, args: WalletHandlerArgs) -> Response:
        user = args.repository.get_user(args.api_key)
        if user is None:
            return Response(
                success=False, message="Invalid Credentials", status_code=401
            )
        args.user = user
        return super().handle(args)


class WalletCountCheckHandler(WalletHandler):
    def handle(self, args: WalletHandlerArgs) -> Response:
        assert args.user is not None
        user_wallets = args.repository.get_user_wallets(args.user)
        if len(user_wallets) >= MAX_WALLET_COUNT:
            return Response(
                success=False,
                message="Max wallet count reached",
                status_code=403,
            )
        return super().handle(args)


class AddWalletHandler(WalletHandler):
    def handle(self, args: WalletHandlerArgs) -> Response:
        assert args.user is not None
        wallet_address = str(uuid.uuid4().hex)
        args.repository.add_wallet(
            Wallet(
                wallet_address=wallet_address,
                btc_balance=DEFAULT_INITIAL_BALANCE,
            ),
            args.user,
        )
        args.wallet_address = wallet_address
        return super().handle(args)


class WalletCheckHandler(WalletHandler):
    def handle(self, args: WalletHandlerArgs) -> Response:
        assert args.user is not None
        assert args.wallet_address is not None
        wallet = args.repository.get_wallet(args.wallet_address)
        if wallet is None or wallet not in args.repository.get_user_wallets(args.user):
            return Response(
                success=False, message="Invalid credentials", status_code=401
            )
        args.wallet = wallet
        return super().handle(args)


class ExchangeRateHandler(WalletHandler):
    def handle(self, args: WalletHandlerArgs) -> Response:
        exchange_rate = get_btc_to_usd_rate()
        if exchange_rate is None:
            return Response(
                success=False,
                message="Could not determine exchange rate",
                status_code=500,
            )
        args.exchange_rate = exchange_rate
        return super().handle(args)
