import uuid
from dataclasses import dataclass
from typing import List, Optional, Protocol

from app.core.repositories import Transaction, UserInfo, Wallet
from app.core.transaction.transaction_interactor import TransactionsResponse
from app.core.utils import Response, get_btc_to_usd_rate

MAX_WALLET_COUNT = 3
DEFAULT_INITIAL_BALANCE = 1.0


@dataclass
class WalletInfo:
    wallet_address: str
    btc_balance: float
    usd_balance: float


@dataclass
class AddWalletRequest:
    api_key: str


@dataclass
class FetchWalletTransactionsRequest:
    api_key: str
    wallet_address: str


@dataclass
class WalletResponse(Response):
    wallet_info: Optional[WalletInfo]


class IWalletRepository(Protocol):
    def get_user(self, api_key: str) -> Optional[UserInfo]:
        pass

    def get_user_wallets(self, user: UserInfo) -> List[Wallet]:
        pass

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
        pass

    def get_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        pass

    def add_wallet(self, wallet: Wallet, user: UserInfo) -> None:
        pass


class IWalletInteractor(Protocol):
    def add_wallet(self, request: AddWalletRequest) -> WalletResponse:
        pass

    def get_wallet_info(self, api_key: str, wallet_address: str) -> WalletResponse:
        pass

    def get_wallet_transactions(
        self, request: FetchWalletTransactionsRequest
    ) -> TransactionsResponse:
        pass


class WalletInteractor:
    def __init__(self, wallet_repository: IWalletRepository):
        self.wallet_repository = wallet_repository

    def add_wallet(self, request: AddWalletRequest) -> WalletResponse:
        user = self.wallet_repository.get_user(request.api_key)
        if user is None:
            return WalletResponse(
                success=False, message="Invalid API key", wallet_info=None
            )
        user_wallets = self.wallet_repository.get_user_wallets(user)
        if len(user_wallets) >= MAX_WALLET_COUNT:
            return WalletResponse(
                success=False, message="Max wallet count reached", wallet_info=None
            )

        wallet_address = str(uuid.uuid4().hex)
        self.wallet_repository.add_wallet(
            Wallet(
                wallet_address=wallet_address,
                btc_balance=DEFAULT_INITIAL_BALANCE,
            ),
            user,
        )
        return self.get_wallet_info(request.api_key, wallet_address)

    def get_wallet_info(self, api_key: str, wallet_address: str) -> WalletResponse:
        user = self.wallet_repository.get_user(api_key)
        wallet = self.wallet_repository.get_wallet(wallet_address)

        if (
            user is None
            or wallet is None
            or wallet not in self.wallet_repository.get_user_wallets(user)
        ):
            return WalletResponse(
                success=False, message="Invalid credentials", wallet_info=None
            )

        exchange_rate = get_btc_to_usd_rate()
        if exchange_rate is None:
            return WalletResponse(
                success=False,
                message="Could not determine exchange rate",
                wallet_info=None,
            )
        usd_balance = wallet.btc_balance * exchange_rate
        wallet_info = WalletInfo(
            wallet_address=wallet_address,
            btc_balance=wallet.btc_balance,
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
        user = self.wallet_repository.get_user(request.api_key)
        wallet = self.wallet_repository.get_wallet(request.wallet_address)

        if (
            user is None
            or wallet is None
            or wallet not in self.wallet_repository.get_user_wallets(user)
        ):
            return TransactionsResponse(
                success=False, message="Invalid credentials", transactions=None
            )

        return TransactionsResponse(
            success=True,
            message="Here are your wallet transactions",
            transactions=self.wallet_repository.get_wallet_transactions(
                request.wallet_address
            ),
        )
