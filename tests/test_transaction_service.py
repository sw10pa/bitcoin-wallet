import os
from typing import Generator

import pytest

from app.core.facade import BTCWalletService
from app.core.transaction.transaction_CoR import FEE_PERCENTAGE, MakeTransactionRequest
from app.core.user.user_interactor import RegisterUserRequest
from app.core.wallet.wallet_CoR import DEFAULT_INITIAL_BALANCE
from app.core.wallet.wallet_interactor import AddWalletRequest, GetWalletRequest
from app.infrastructure.sqlite.sqlite_repository import SQLiteRepository
from tests.test_sqlite_repository import TEST_DB_NAME


def test_get_user_transactions_invalid_credentials(service: BTCWalletService) -> None:
    response = service.get_transactions("")
    assert response.success is False
    assert response.status_code == 401
    assert response.transactions is None


def test_make_transaction_invalid_credentials(service: BTCWalletService) -> None:
    response = service.make_transaction(MakeTransactionRequest("", "", "", 0))
    assert response.success is False
    assert response.status_code == 401


def test_get_user_transactions_empty(service: BTCWalletService) -> None:
    register_response = service.register_user(RegisterUserRequest("test"))
    assert register_response.api_key is not None
    response = service.get_transactions(register_response.api_key)
    assert response.success is True
    assert response.status_code == 200
    assert response.transactions == []


def test_make_transaction_same_user(service: BTCWalletService) -> None:
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

    response = service.get_transactions(api_key)

    assert response.success is True
    assert response.status_code == 200
    assert response.transactions is not None
    assert len(response.transactions) == 1
    assert response.transactions[0].wallet_address_from == wallet_address_1
    assert response.transactions[0].wallet_address_to == wallet_address_2
    assert response.transactions[0].btc_amount == btc_amount
    assert response.transactions[0].fee_pct == 0.0
    assert response.transactions[0].exchange_rate is not None

    wallet_response = service.get_wallet(GetWalletRequest(api_key, wallet_address_1))
    assert wallet_response.success is True
    assert wallet_response.status_code == 200
    assert wallet_response.wallet_info is not None
    assert (
        wallet_response.wallet_info.btc_balance == DEFAULT_INITIAL_BALANCE - btc_amount
    )

    wallet_response = service.get_wallet(GetWalletRequest(api_key, wallet_address_2))
    assert wallet_response.success is True
    assert wallet_response.status_code == 200
    assert wallet_response.wallet_info is not None
    assert (
        wallet_response.wallet_info.btc_balance == DEFAULT_INITIAL_BALANCE + btc_amount
    )


def test_make_transaction_different_user(service: BTCWalletService) -> None:
    register_response = service.register_user(RegisterUserRequest("test_email_1"))
    assert register_response.api_key is not None
    api_key_1 = register_response.api_key

    register_response = service.register_user(RegisterUserRequest("test_email_2"))
    assert register_response.api_key is not None
    api_key_2 = register_response.api_key

    wallet_response = service.add_wallet(AddWalletRequest(api_key=api_key_1))
    assert wallet_response.wallet_info is not None
    wallet_address_1 = wallet_response.wallet_info.wallet_address

    wallet_response = service.add_wallet(AddWalletRequest(api_key=api_key_2))
    assert wallet_response.wallet_info is not None
    wallet_address_2 = wallet_response.wallet_info.wallet_address

    btc_amount = 0.1
    make_transaction_response = service.make_transaction(
        MakeTransactionRequest(
            api_key=api_key_1,
            wallet_address_from=wallet_address_1,
            wallet_address_to=wallet_address_2,
            btc_amount=btc_amount,
        )
    )
    assert make_transaction_response.success is True
    assert make_transaction_response.status_code == 200

    response = service.get_transactions(api_key_1)

    assert response.success is True
    assert response.status_code == 200
    assert response.transactions is not None
    assert len(response.transactions) == 1
    assert response.transactions[0].wallet_address_from == wallet_address_1
    assert response.transactions[0].wallet_address_to == wallet_address_2
    assert response.transactions[0].btc_amount == btc_amount
    assert response.transactions[0].fee_pct == FEE_PERCENTAGE
    assert response.transactions[0].exchange_rate is not None

    response = service.get_transactions(api_key_2)

    assert response.success is True
    assert response.status_code == 200
    assert response.transactions is not None
    assert len(response.transactions) == 1
    assert response.transactions[0].wallet_address_from == wallet_address_1
    assert response.transactions[0].wallet_address_to == wallet_address_2
    assert response.transactions[0].btc_amount == btc_amount
    assert response.transactions[0].fee_pct == FEE_PERCENTAGE
    assert response.transactions[0].exchange_rate is not None

    wallet_response = service.get_wallet(GetWalletRequest(api_key_1, wallet_address_1))
    assert wallet_response.success is True
    assert wallet_response.status_code == 200
    assert wallet_response.wallet_info is not None
    assert (
        wallet_response.wallet_info.btc_balance == DEFAULT_INITIAL_BALANCE - btc_amount
    )

    wallet_response = service.get_wallet(GetWalletRequest(api_key_2, wallet_address_2))
    assert wallet_response.success is True
    assert wallet_response.status_code == 200
    assert wallet_response.wallet_info is not None
    assert (
        wallet_response.wallet_info.btc_balance
        == DEFAULT_INITIAL_BALANCE + (1 - FEE_PERCENTAGE) * btc_amount
    )


@pytest.fixture
def service() -> Generator[BTCWalletService, None, None]:
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)

    repository = SQLiteRepository(db_name=TEST_DB_NAME)
    yield BTCWalletService.create(repository, repository, repository, repository)
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)
