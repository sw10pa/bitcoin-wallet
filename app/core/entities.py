from dataclasses import dataclass


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


@dataclass
class Wallet:
    wallet_address: str
    btc_balance: float

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Wallet):
            return self.wallet_address == other.wallet_address
        return False
