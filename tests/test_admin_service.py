import os
from typing import Generator

import pytest

from app.core.admin.admin_interactor import StatisticsRequest, StatisticsResponse
from app.core.facade import BTCWalletService
from app.core.transaction.transaction_CoR import FEE_PERCENTAGE, MakeTransactionRequest
from app.core.user.user_interactor import RegisterUserRequest
from app.core.wallet.wallet_interactor import AddWalletRequest
from app.infrastructure.sqlite.sqlite_repository import SQLiteRepository
from tests.test_sqlite_repository import TEST_DB_NAME

ADMIN_API_KEY = "Stephane27"


def test_statistics_invalid_credentials(service: BTCWalletService) -> None:
    request = StatisticsRequest(api_key="")
    response: StatisticsResponse = service.get_statistics(request=request)

    assert response.success is False
    assert response.status_code == 401
    assert response.statistics_info is None


def test_statistics_valid_credentials(service: BTCWalletService) -> None:
    request = StatisticsRequest(api_key=ADMIN_API_KEY)
    response: StatisticsResponse = service.get_statistics(request=request)

    assert response.success is True
    assert response.status_code == 200
    assert response.statistics_info is not None


def test_empty_statistics(service: BTCWalletService) -> None:
    request = StatisticsRequest(api_key=ADMIN_API_KEY)
    response: StatisticsResponse = service.get_statistics(request=request)

    assert response.success is True
    assert response.status_code == 200
    assert response.statistics_info is not None
    assert response.statistics_info.total_btc_profit == 0
    assert response.statistics_info.total_transaction_count == 0


def test_valid_statistics(service: BTCWalletService) -> None:
    register_response = service.register_user(RegisterUserRequest("test_email_1"))
    assert register_response.api_key is not None
    api_key_1 = register_response.api_key

    register_response = service.register_user(RegisterUserRequest("test_email_2"))
    assert register_response.api_key is not None
    api_key_2 = register_response.api_key

    wallet_response = service.add_wallet(AddWalletRequest(api_key=api_key_1))
    assert wallet_response.wallet_info is not None
    wallet_address_1_1 = wallet_response.wallet_info.wallet_address

    wallet_response = service.add_wallet(AddWalletRequest(api_key=api_key_1))
    assert wallet_response.wallet_info is not None
    wallet_address_1_2 = wallet_response.wallet_info.wallet_address

    wallet_response = service.add_wallet(AddWalletRequest(api_key=api_key_2))
    assert wallet_response.wallet_info is not None
    wallet_address_2_1 = wallet_response.wallet_info.wallet_address

    service.make_transaction(
        MakeTransactionRequest(
            api_key=api_key_1,
            wallet_address_from=wallet_address_1_1,
            wallet_address_to=wallet_address_1_2,
            btc_amount=0.1,
        )
    )

    response = service.get_statistics(StatisticsRequest(api_key=ADMIN_API_KEY))

    assert response.success is True
    assert response.status_code == 200
    assert response.statistics_info is not None
    assert response.statistics_info.total_btc_profit == 0
    assert response.statistics_info.total_transaction_count == 1

    service.make_transaction(
        MakeTransactionRequest(
            api_key=api_key_1,
            wallet_address_from=wallet_address_1_2,
            wallet_address_to=wallet_address_2_1,
            btc_amount=1,
        )
    )

    response = service.get_statistics(StatisticsRequest(api_key=ADMIN_API_KEY))

    assert response.success is True
    assert response.status_code == 200
    assert response.statistics_info is not None
    assert response.statistics_info.total_btc_profit == 1 * FEE_PERCENTAGE
    assert response.statistics_info.total_transaction_count == 2


@pytest.fixture
def service() -> Generator[BTCWalletService, None, None]:
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)
    repository = SQLiteRepository(db_name=TEST_DB_NAME)
    yield BTCWalletService.create(repository, repository, repository, repository)
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)
