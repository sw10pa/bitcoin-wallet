import os
from typing import Generator

import pytest

from app.core.facade import BTCWalletService
from app.core.transaction.transaction_CoR import MakeTransactionRequest
from app.core.user.user_interactor import RegisterUserRequest
from app.core.wallet.wallet_CoR import DEFAULT_INITIAL_BALANCE, MAX_WALLET_COUNT
from app.core.wallet.wallet_interactor import (
    AddWalletRequest,
    FetchWalletTransactionsRequest,
    GetWalletRequest,
)
from app.infrastructure.sqlite.sqlite_repository import SQLiteRepository
from tests.test_sqlite_repository import TEST_DB_NAME


def test_add_wallet_invalid_credentials(service: BTCWalletService) -> None:
    response = service.add_wallet(AddWalletRequest(api_key=""))
    assert response.success is False
    assert response.status_code == 401
    assert response.wallet_info is None


def test_get_wallet_invalid_credentials(service: BTCWalletService) -> None:
    response = service.get_wallet(GetWalletRequest("", ""))
    assert response.success is False
    assert response.status_code == 401
    assert response.wallet_info is None


def test_get_wallet_transactions_invalid_credentials(service: BTCWalletService) -> None:
    response = service.get_wallet_transactions(FetchWalletTransactionsRequest("", ""))
    assert response.success is False
    assert response.status_code == 401
    assert response.transactions is None


def test_add_wallet_success(service: BTCWalletService) -> None:
    user_response = service.register_user(RegisterUserRequest("test_email"))
    assert user_response.api_key is not None
    response = service.add_wallet(AddWalletRequest(api_key=user_response.api_key))
    assert response.success is True
    assert response.status_code == 200
    assert response.wallet_info is not None
    assert response.wallet_info.wallet_address is not None
    assert response.wallet_info.btc_balance is not None
    assert response.wallet_info.btc_balance == DEFAULT_INITIAL_BALANCE
    assert response.wallet_info.usd_balance is not None


def test_add_wallet_more_than_limit(service: BTCWalletService) -> None:
    user_response = service.register_user(RegisterUserRequest("test_email"))
    assert user_response.api_key is not None
    for _ in range(MAX_WALLET_COUNT):
        response = service.add_wallet(AddWalletRequest(api_key=user_response.api_key))
        assert response.success is True

    response = service.add_wallet(AddWalletRequest(api_key=user_response.api_key))
    assert response.success is False
    assert response.status_code == 403
    assert response.wallet_info is None


def test_get_wallet_initial_wallet(service: BTCWalletService) -> None:
    user_response = service.register_user(RegisterUserRequest("test_email"))
    assert user_response.api_key is not None
    response = service.add_wallet(AddWalletRequest(api_key=user_response.api_key))
    assert response.wallet_info is not None
    assert response.wallet_info.wallet_address is not None
    response = service.get_wallet(
        GetWalletRequest(user_response.api_key, response.wallet_info.wallet_address)
    )
    assert response.success is True
    assert response.status_code == 200
    assert response.wallet_info is not None
    assert response.wallet_info.wallet_address is not None
    assert response.wallet_info.btc_balance is not None
    assert response.wallet_info.btc_balance == DEFAULT_INITIAL_BALANCE
    assert response.wallet_info.usd_balance is not None


def test_get_wallet_transactions_empty(service: BTCWalletService) -> None:
    user_response = service.register_user(RegisterUserRequest("test_email"))
    assert user_response.api_key is not None
    add_wallet_response = service.add_wallet(
        AddWalletRequest(api_key=user_response.api_key)
    )
    assert add_wallet_response.wallet_info is not None
    assert add_wallet_response.wallet_info.wallet_address is not None
    response = service.get_wallet_transactions(
        FetchWalletTransactionsRequest(
            user_response.api_key, add_wallet_response.wallet_info.wallet_address
        )
    )
    assert response.success is True
    assert response.status_code == 200
    assert response.transactions is not None
    assert len(response.transactions) == 0
    assert response.transactions == []


def test_get_wallet_transactions_with_transactions(service: BTCWalletService) -> None:
    register_response = service.register_user(RegisterUserRequest("test_email"))
    assert register_response.api_key is not None
    api_key = register_response.api_key

    wallet_response = service.add_wallet(AddWalletRequest(api_key=api_key))
    assert wallet_response.wallet_info is not None
    wallet_address_1 = wallet_response.wallet_info.wallet_address

    wallet_response = service.add_wallet(AddWalletRequest(api_key=api_key))
    assert wallet_response.wallet_info is not None
    wallet_address_2 = wallet_response.wallet_info.wallet_address

    btc_amount = 0.1
    make_transaction_response = service.make_transaction(
        MakeTransactionRequest(
            api_key=api_key,
            wallet_address_from=wallet_address_1,
            wallet_address_to=wallet_address_2,
            btc_amount=btc_amount,
        )
    )
    assert make_transaction_response.success is True
    assert make_transaction_response.status_code == 200

    response = service.get_wallet_transactions(
        FetchWalletTransactionsRequest(api_key, wallet_address_1)
    )
    assert response.success is True
    assert response.status_code == 200
    assert response.transactions is not None
    assert len(response.transactions) == 1
    assert response.transactions[0].btc_amount == btc_amount
    assert response.transactions[0].wallet_address_from == wallet_address_1
    assert response.transactions[0].wallet_address_to == wallet_address_2

    response = service.get_wallet_transactions(
        FetchWalletTransactionsRequest(api_key, wallet_address_2)
    )
    assert response.success is True
    assert response.status_code == 200
    assert response.transactions is not None
    assert len(response.transactions) == 1
    assert response.transactions[0].btc_amount == btc_amount
    assert response.transactions[0].wallet_address_from == wallet_address_1
    assert response.transactions[0].wallet_address_to == wallet_address_2


@pytest.fixture
def service() -> Generator[BTCWalletService, None, None]:
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)

    repository = SQLiteRepository(db_name=TEST_DB_NAME)
    yield BTCWalletService.create(repository, repository, repository, repository)
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)
