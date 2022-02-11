from dataclasses import dataclass
from typing import List, Optional, Protocol


@dataclass
class Wallet:
    wallet_address: str
    btc_balance: float

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Wallet):
            return self.wallet_address == other.wallet_address
        return False


@dataclass
class Transaction:
    wallet_address_from: str
    wallet_address_to: str
    btc_amount: float
    fee_pct: float
    exchange_rate: float


@dataclass
class StatisticsInfo:
    total_transaction_count: int
    total_btc_profit: float


@dataclass
class UserInfo:
    api_key: str
    email: str

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UserInfo):
            return self.api_key == other.api_key
        return False


class IFatherRepository(Protocol):
    def register_user(self, user: UserInfo) -> None:
        pass

    def fetch_all_transactions(self) -> List[Transaction]:
        pass

    # saves transaction in database
    def add_transaction(self, transaction: Transaction) -> None:
        pass

    # gets all user related transactions out of all wallets that belong to user
    def get_user_transactions(self, user: UserInfo) -> List[Transaction]:
        pass

    def get_wallet_user(self, wallet_address: str) -> UserInfo:
        pass

    def add_wallet(self, wallet: Wallet, user: UserInfo) -> None:
        pass

    def get_wallet(self, wallet_address: str) -> Wallet:
        pass

    # gets incoming and outgoing transactions that are related to this wallet
    def get_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        pass

    def update_wallet_balance(
        self, wallet_address: str, new_btc_balance: float
    ) -> None:
        pass

    def get_user(self, api_key: str) -> Optional[UserInfo]:
        pass

    def get_user_by_email(self, email: str) -> Optional[UserInfo]:
        pass

    def get_user_wallets(self, user: UserInfo) -> List[Wallet]:
        pass
