from app.core.admin.admin_interactor import (
    AdminInteractor,
    IAdminInteractor,
    StatisticsRequest,
    StatisticsResponse,
)
from app.core.admin.admin_repository import IAdminRepository
from app.core.transaction.transaction_CoR import MakeTransactionRequest
from app.core.transaction.transaction_interactor import (
    ITransactionInteractor,
    TransactionInteractor,
    TransactionsResponse,
)
from app.core.transaction.transaction_repository import ITransactionRepository
from app.core.user.user_interactor import (
    IUserInteractor,
    RegisterUserRequest,
    RegisterUserResponse,
    UserInteractor,
)
from app.core.user.user_repository import IUserRepository
from app.core.utils import Response
from app.core.wallet.wallet_interactor import (
    AddWalletRequest,
    FetchWalletTransactionsRequest,
    IWalletInteractor,
    WalletInteractor,
    WalletResponse,
)
from app.core.wallet.wallet_repository import IWalletRepository


class BTCWalletService:
    _admin_interactor: IAdminInteractor
    _transaction_interactor: ITransactionInteractor
    _user_interactor: IUserInteractor
    _wallet_interactor: IWalletInteractor

    def __init__(
        self,
        admin_interactor: IAdminInteractor,
        transaction_interactor: ITransactionInteractor,
        user_interactor: IUserInteractor,
        wallet_interactor: IWalletInteractor,
    ):
        self._admin_interactor = admin_interactor
        self._transaction_interactor = transaction_interactor
        self._user_interactor = user_interactor
        self._wallet_interactor = wallet_interactor

    @classmethod
    def create(
        cls,
        admin_repository: IAdminRepository,
        transaction_repository: ITransactionRepository,
        user_repository: IUserRepository,
        wallet_reporsitory: IWalletRepository,
    ) -> "BTCWalletService":
        return cls(
            AdminInteractor(admin_repository),
            TransactionInteractor(transaction_repository),
            UserInteractor(user_repository),
            WalletInteractor(wallet_reporsitory),
        )

    def get_statistics(self, request: StatisticsRequest) -> StatisticsResponse:
        return self._admin_interactor.get_statistics(request)

    def add_wallet(self, request: AddWalletRequest) -> WalletResponse:
        return self._wallet_interactor.add_wallet(request)

    def get_wallet(self, api_key: str, address: str) -> WalletResponse:
        return self._wallet_interactor.get_wallet_info(api_key, address)

    def get_wallet_transactions(
        self, request: FetchWalletTransactionsRequest
    ) -> TransactionsResponse:
        return self._wallet_interactor.get_wallet_transactions(request)

    def register_user(self, request: RegisterUserRequest) -> RegisterUserResponse:
        return self._user_interactor.register_user(request)

    def get_transactions(self, api_key: str) -> TransactionsResponse:
        return self._transaction_interactor.get_user_transactions(api_key)

    def make_transaction(self, request: MakeTransactionRequest) -> Response:
        return self._transaction_interactor.make_transaction(request)
