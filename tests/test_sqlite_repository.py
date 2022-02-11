import os

from app.core.repositories import Transaction, UserInfo, Wallet
from app.infrastructure.sqlite.sqlite_repository import SQLiteRepository

TEST_DB_NAME = "tst.db"


def test_should_create_sqlite_repository() -> None:
    if os.path.exists(TEST_DB_NAME):
        os.remove(TEST_DB_NAME)

    SQLiteRepository(db_name=TEST_DB_NAME)


def test_should_fill_tables_with_test_data() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    sqlite_repository.register_user(user=UserInfo(api_key="api_key_1", email="email_1"))
    sqlite_repository.register_user(user=UserInfo(api_key="api_key_2", email="email_2"))

    sqlite_repository.add_wallet(
        wallet=Wallet(wallet_address="wallet_address_1", btc_balance=1),
        user=UserInfo(api_key="api_key_1", email="email_1"),
    )
    sqlite_repository.add_wallet(
        wallet=Wallet(wallet_address="wallet_address_2", btc_balance=2),
        user=UserInfo(api_key="api_key_2", email="email_2"),
    )

    sqlite_repository.add_transaction(
        transaction=Transaction(
            wallet_address_from="wallet_address_1",
            wallet_address_to="wallet_address_2",
            btc_amount=1,
            fee_pct=1,
            exchange_rate=1,
        )
    )
    sqlite_repository.add_transaction(
        transaction=Transaction(
            wallet_address_from="wallet_address_1",
            wallet_address_to="wallet_address_1",
            btc_amount=2,
            fee_pct=2,
            exchange_rate=2,
        )
    )

    sqlite_repository.add_transaction(
        transaction=Transaction(
            wallet_address_from="wallet_address_2",
            wallet_address_to="wallet_address_1",
            btc_amount=3,
            fee_pct=3,
            exchange_rate=3,
        )
    )
    sqlite_repository.add_transaction(
        transaction=Transaction(
            wallet_address_from="wallet_address_2",
            wallet_address_to="wallet_address_2",
            btc_amount=4,
            fee_pct=4,
            exchange_rate=4,
        )
    )


def test_should_fetch_all_transactions() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    transactions = sqlite_repository.fetch_all_transactions()
    assert len(transactions) == 4

    for i in range(1, 5):
        transaction = transactions[i - 1]

        if i == 1:
            assert transaction.wallet_address_from == "wallet_address_1"
            assert transaction.wallet_address_to == "wallet_address_2"
        elif i == 2:
            assert transaction.wallet_address_from == "wallet_address_1"
            assert transaction.wallet_address_to == "wallet_address_1"
        elif i == 3:
            assert transaction.wallet_address_from == "wallet_address_2"
            assert transaction.wallet_address_to == "wallet_address_1"
        else:
            assert transaction.wallet_address_from == "wallet_address_2"
            assert transaction.wallet_address_to == "wallet_address_2"

        assert transaction.btc_amount == i
        assert transaction.fee_pct == i
        assert transaction.exchange_rate == i


def test_should_get_user_transactions() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    transactions = sqlite_repository.get_user_transactions(
        user=UserInfo(api_key="api_key_1", email="email_1")
    )
    assert len(transactions) == 3

    for i in range(1, 4):
        transaction = transactions[i - 1]

        if i == 1:
            assert transaction.wallet_address_from == "wallet_address_1"
            assert transaction.wallet_address_to == "wallet_address_2"
        elif i == 2:
            assert transaction.wallet_address_from == "wallet_address_1"
            assert transaction.wallet_address_to == "wallet_address_1"
        else:
            assert transaction.wallet_address_from == "wallet_address_2"
            assert transaction.wallet_address_to == "wallet_address_1"

        assert transaction.btc_amount == i
        assert transaction.fee_pct == i
        assert transaction.exchange_rate == i


def test_should_get_wallet_user() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    user = sqlite_repository.get_wallet_user(wallet_address="wallet_address_1")

    assert user.api_key == "api_key_1"
    assert user.email == "email_1"


def test_should_get_wallet() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    wallet = sqlite_repository.get_wallet(wallet_address="wallet_address_1")

    assert wallet.wallet_address == "wallet_address_1"
    assert wallet.btc_balance == 1


def test_should_get_wallet_transactions() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    transactions = sqlite_repository.get_wallet_transactions(
        wallet_address="wallet_address_1"
    )
    assert len(transactions) == 3

    for i in range(1, 4):
        transaction = transactions[i - 1]

        if i == 1:
            assert transaction.wallet_address_from == "wallet_address_1"
            assert transaction.wallet_address_to == "wallet_address_2"
        elif i == 2:
            assert transaction.wallet_address_from == "wallet_address_1"
            assert transaction.wallet_address_to == "wallet_address_1"
        else:
            assert transaction.wallet_address_from == "wallet_address_2"
            assert transaction.wallet_address_to == "wallet_address_1"

        assert transaction.btc_amount == i
        assert transaction.fee_pct == i
        assert transaction.exchange_rate == i


def test_should_update_wallet_balance() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    sqlite_repository.update_wallet_balance(
        wallet_address="wallet_address_1", new_btc_balance=2
    )

    wallet = sqlite_repository.get_wallet(wallet_address="wallet_address_1")

    assert wallet.wallet_address == "wallet_address_1"
    assert wallet.btc_balance == 2


def test_should_get_user() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    user = sqlite_repository.get_user(api_key="api_key_1")
    assert user is not None

    assert user.api_key == "api_key_1"
    assert user.email == "email_1"


def test_should_get_user_by_email() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    user = sqlite_repository.get_user_by_email(email="email_1")
    assert user is not None

    assert user.api_key == "api_key_1"
    assert user.email == "email_1"


def test_should_get_user_wallets() -> None:
    sqlite_repository = SQLiteRepository(db_name=TEST_DB_NAME)

    wallets = sqlite_repository.get_user_wallets(
        user=UserInfo(api_key="api_key_1", email="email_1")
    )
    assert len(wallets) == 1

    assert wallets[0].wallet_address == "wallet_address_1"
    assert wallets[0].btc_balance == 2
