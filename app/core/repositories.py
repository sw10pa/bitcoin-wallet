from dataclasses import dataclass
from typing import Protocol, List


@dataclass
class WalletInfo:
    wallet_address: str
    btc_balance: float
    usd_balance: float

@dataclass
class Transaction:
    wallet_address_from: str
    wallet_address_to: str
    btc_amount: float
    fee_amount: float
    exchange_rate: float


class IFatherRepository(Protocol):
    def register_user(self, email: str) -> str:
        pass

    def add_wallet(self, api_key: str) -> WalletInfo:
        pass

    def get_wallet(self, wallet_address: str) -> WalletInfo:
        pass

    def make_transaction(self, api_key: str, transaction: Transaction) -> None:
        pass

    def get_user_transactions(self, api_key: str) -> List[Transaction]:
        pass

    def get_wallet_transactions(self, api_key: str, wallet_address: str) -> List[Transaction]:
        pass

    # def get_statistics(self): TODO