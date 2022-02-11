from dataclasses import dataclass
from typing import Protocol

from app.core.facade import Response
from app.core.repositories import IFatherRepository, Wallet
from app.core.transaction.transaction_interactor import TransactionsResponse


@dataclass
class WalletInfo:
    wallet_address: str
    btc_balance: float
    usd_balance: float


@dataclass
class AddWalletRequest:
    api_key: str


@dataclass
class WalletResponse(Response):
    wallet_info: WalletInfo


class IWalletInteractor(Protocol):
    def get_wallet_info(self, wallet_address: str) -> WalletResponse:
        pass

    def add_wallet(self, request: AddWalletRequest) -> WalletResponse:
        pass

    # TODO Request
    def get_wallet_transactions(
        self, api_key: str, wallet_address: str
    ) -> TransactionsResponse:
        pass


class WalletInteractor:
    def __init__(
        self, wallet_repository: IFatherRepository
    ):  # TODO Change to IWalletRepository
        self.wallet_repository = wallet_repository

    def get_wallet_info(self, wallet_address: str) -> WalletResponse:
        wallet = self.wallet_repository.get_wallet(wallet_address)
        usd_balance = wallet.btc_balance * 1.7
        # TODO convert to usd
        wallet_info = WalletInfo(
            wallet_address=wallet_address,
            btc_balance=wallet.btc_balance,
            usd_balance=usd_balance,
        )
        return WalletResponse(success=True, message="TODO", wallet_info=wallet_info)

    def add_wallet(self, request: AddWalletRequest) -> WalletResponse:
        # TODO Generate wallet_address
        wallet_address = "TODO"
        wallet_btc_balance = 0  # TODO add starting balance
        # TODO convert to usd
        wallet_info = WalletInfo(
            wallet_address=wallet_address,
            btc_balance=wallet_btc_balance,
            usd_balance=wallet_btc_balance * 1.7,
        )
        self.wallet_repository.add_wallet(
            Wallet(wallet_address, wallet_btc_balance), request.api_key
        )
        return WalletResponse(
            success=True,
            message="TODO",
            wallet_info=wallet_info,
        )

    def get_wallet_transactions(
        self, api_key: str, wallet_address: str
    ) -> TransactionsResponse:
        # TODO check valid
        return TransactionsResponse(
            success=True,
            message="TODO",
            transactions=self.wallet_repository.get_wallet_transactions(wallet_address),
        )
