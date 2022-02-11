from dataclasses import dataclass
from typing import List, Protocol


@dataclass
class Wallet:
    wallet_address: str
    btc_balance: float


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


class IFatherRepository(Protocol):
    def register_user(self, user: UserInfo) -> None:
        pass

    def fetch_all_transactions(self) -> List[Transaction]:
        pass

    # saves transaction in databse
    def add_transaction(self, transaction: Transaction) -> None:
        pass

    # gets all user related transactions out of all wallets that belong to user
    def get_user_transactions(self, api_key: str) -> List[Transaction]:
        pass

    def get_wallet_user(self, wallet_address: str) -> UserInfo:
        pass

    def add_wallet(self, wallet: Wallet, user_api_key: str) -> None:
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
