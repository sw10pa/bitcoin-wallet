import os
from typing import Generator

import pytest

from app.core.facade import BTCWalletService
from app.core.user.user_interactor import RegisterUserRequest
from app.infrastructure.sqlite.sqlite_repository import SQLiteRepository
from tests.test_sqlite_repository import TEST_DB_NAME


def test_create_user(service: BTCWalletService) -> None:
    response = service.register_user(RegisterUserRequest(email="test_email"))
    assert response.success is True
    assert response.api_key is not None
    assert response.api_key != ""
    assert response.status_code == 201


def test_create_user_with_existing_email(service: BTCWalletService) -> None:
    response = service.register_user(RegisterUserRequest(email="test_email"))
    assert response.success is True
    assert response.api_key is not None
    assert response.status_code == 201

    response = service.register_user(RegisterUserRequest(email="test_email"))
    assert response.success is False
    assert response.api_key is None
    assert response.status_code == 409


def test_user_initialization(service: BTCWalletService) -> None:
    response = service.register_user(RegisterUserRequest(email="test_email"))
    assert response.success is True
    assert response.api_key is not None
    assert response.status_code == 201

    transactions_response = service.get_transactions(response.api_key)
    assert transactions_response.success is True
    assert transactions_response.transactions == []


@pytest.fixture
def service() -> Generator[BTCWalletService, None, None]:
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)

    repository = SQLiteRepository(db_name=TEST_DB_NAME)
    yield BTCWalletService.create(repository, repository, repository, repository)
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)
