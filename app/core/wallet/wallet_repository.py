from typing import List, Optional, Protocol

from app.core.entities import Transaction, UserInfo, Wallet


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
