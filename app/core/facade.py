from dataclasses import dataclass

from app.core.admin.admin_interactor import StatisticsRequest, StatisticsResponse
from app.core.transaction.transaction_interactor import (
    MakeTransactionRequest,
    TransactionsResponse,
)
from app.core.user.user_interactor import RegisterUserRequest, RegisterUserResponse
from app.core.wallet.wallet_interactor import WalletResponse


@dataclass
class Response:
    success: bool
    message: str


class BTCWalletService:
    # _admin_interactor: IAdminInteractor
    # _transaction_interactor: ITransactionInteractor
    # _user_interactor: IUserInteractor
    # _wallet_interactor: IWalle    tInteractor
    #
    # def __init__(
    #     self, store_interactor: IStoreInteractor, receipt_interactor: IReceiptInteractor
    # ):
    #     self._store_interactor = store_interactor
    #     self._receipt_interactor = receipt_interactor

    @classmethod
    def create(cls) -> "BTCWalletService":
        return cls()

    def get_statistics(self, request: StatisticsRequest) -> StatisticsResponse:
        pass

    def add_wallet(self, api_key: str) -> WalletResponse:
        pass

    def get_wallet(self, api_key: str, address: str) -> WalletResponse:
        pass

    def get_wallet_transactions(
        self, api_key: str, address: str
    ) -> TransactionsResponse:
        pass

    def register_user(self, request: RegisterUserRequest) -> RegisterUserResponse:
        pass

    def get_transactions(self, api_key: str) -> TransactionsResponse:
        pass

    def make_transaction(self, request: MakeTransactionRequest) -> Response:
        pass
