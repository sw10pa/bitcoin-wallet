from typing import List, Optional, Protocol

from app.core.repositories import Transaction, UserInfo, Wallet


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
