from dataclasses import dataclass
from typing import Optional, Protocol

from app.core.transaction.transaction_interactor import TransactionsResponse
from app.core.utils import Response
from app.core.wallet.wallet_CoR import (
    AddWalletHandler,
    ExchangeRateHandler,
    UserCheckHandler,
    WalletCheckHandler,
    WalletCountCheckHandler,
    WalletHandlerArgs,
)
from app.core.wallet.wallet_repository import IWalletRepository


@dataclass
class WalletInfo:
    wallet_address: str
    btc_balance: float
    usd_balance: float


@dataclass
class AddWalletRequest:
    api_key: str


@dataclass
class GetWalletRequest:
    api_key: str
    wallet_address: str


@dataclass
class FetchWalletTransactionsRequest:
    api_key: str
    wallet_address: str


@dataclass
class WalletResponse(Response):
    wallet_info: Optional[WalletInfo]


class IWalletInteractor(Protocol):
    def add_wallet(self, request: AddWalletRequest) -> WalletResponse:
        pass

    def get_wallet_info(self, request: GetWalletRequest) -> WalletResponse:
        pass

    def get_wallet_transactions(
        self, request: FetchWalletTransactionsRequest
    ) -> TransactionsResponse:
        pass


class WalletInteractor:
    def __init__(self, wallet_repository: IWalletRepository):
        self.wallet_repository = wallet_repository

    def add_wallet(self, request: AddWalletRequest) -> WalletResponse:
        handler = UserCheckHandler()
        handler.set_next(WalletCountCheckHandler()).set_next(AddWalletHandler())
        args = WalletHandlerArgs(
            api_key=request.api_key, repository=self.wallet_repository
        )

        response = handler.handle(args)
        if not response.success:
            return WalletResponse(
                success=response.success, message=response.message, wallet_info=None
            )
        assert args.wallet_address is not None
        return self.get_wallet_info(
            GetWalletRequest(request.api_key, args.wallet_address)
        )

    def get_wallet_info(self, request: GetWalletRequest) -> WalletResponse:
        handler = UserCheckHandler()
        handler.set_next(WalletCheckHandler()).set_next(ExchangeRateHandler())
        args = WalletHandlerArgs(
            api_key=request.api_key,
            repository=self.wallet_repository,
            wallet_address=request.wallet_address,
        )
        response = handler.handle(args)

        if not response.success:
            return WalletResponse(
                success=response.success, message=response.message, wallet_info=None
            )
        assert args.wallet is not None
        assert args.exchange_rate is not None

        usd_balance = args.wallet.btc_balance * args.exchange_rate
        wallet_info = WalletInfo(
            wallet_address=request.wallet_address,
            btc_balance=args.wallet.btc_balance,
            usd_balance=usd_balance,
        )
        return WalletResponse(
            success=True,
            message="Here is your wallet information",
            wallet_info=wallet_info,
        )

    def get_wallet_transactions(
        self, request: FetchWalletTransactionsRequest
    ) -> TransactionsResponse:
        handler = UserCheckHandler()
        handler.set_next(WalletCheckHandler())
        args = WalletHandlerArgs(
            api_key=request.api_key,
            repository=self.wallet_repository,
            wallet_address=request.wallet_address,
        )

        response = handler.handle(args)
        if not response.success:
            return TransactionsResponse(
                success=response.success, message=response.message, transactions=None
            )

        return TransactionsResponse(
            success=True,
            message="Here are your wallet transactions",
            transactions=self.wallet_repository.get_wallet_transactions(
                request.wallet_address
            ),
        )
