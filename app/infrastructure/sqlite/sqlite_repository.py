import sqlite3
from sqlite3 import Cursor
from typing import List, Optional

from app.core.repositories import Transaction, UserInfo, Wallet


class SQLiteRepository:
    def __init__(self, db_name: str = "bw.db") -> None:
        self.db_name = db_name
        self.__create_tables()

    def __create_tables(self) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY,
               email TEXT NOT NULL UNIQUE,
               api_key TEXT NOT NULL UNIQUE);"""
        )
        connection.commit()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS wallets (
               id INTEGER PRIMARY KEY,
               address TEXT NOT NULL UNIQUE,
               balance_in_btc FLOAT NOT NULL);"""
        )
        connection.commit()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users_wallets (
               id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               wallet_id INTEGER NOT NULL);"""
        )
        connection.commit()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS transactions (
               id INTEGER PRIMARY KEY,
               wallet_id_from INTEGER NOT NULL,
               wallet_id_to INTEGER NOT NULL,
               amount_in_btc FLOAT NOT NULL,
               fee_pct FLOAT,
               btc_usd_exchange_rate FLOAT NOT NULL);"""
        )
        connection.commit()

        cursor.close()
        connection.close()

    def register_user(self, user: UserInfo) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """INSERT INTO users (email, api_key)
                     VALUES (?, ?);"""
        args = (user.email, user.api_key)

        cursor.execute(command, args)
        connection.commit()

        cursor.close()
        connection.close()

    def fetch_all_transactions(self) -> List[Transaction]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT w1.address,
                            w2.address,
                            t.amount_in_btc,
                            t.fee_pct,
                            t.btc_usd_exchange_rate
                     FROM transactions t
                     JOIN wallets w1
                     ON t.wallet_id_from = w1.id
                     JOIN wallets w2
                     ON t.wallet_id_to = w2.id;"""

        cursor.execute(command)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        transactions = []

        if rows:
            for row in rows:
                transactions.append(
                    Transaction(
                        wallet_address_from=row[0],
                        wallet_address_to=row[1],
                        btc_amount=row[2],
                        fee_pct=row[3],
                        exchange_rate=row[4],
                    )
                )

        return transactions

    def add_transaction(self, transaction: Transaction) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        wallet_id_from = self.__get_wallet_id(
            cursor=cursor, wallet_address=transaction.wallet_address_from
        )
        wallet_id_to = self.__get_wallet_id(
            cursor=cursor, wallet_address=transaction.wallet_address_to
        )

        command = """INSERT INTO transactions (wallet_id_from, wallet_id_to, amount_in_btc, fee_pct, btc_usd_exchange_rate)
                     VALUES (?, ?, ?, ?, ?);"""
        args = (
            wallet_id_from,
            wallet_id_to,
            transaction.btc_amount,
            transaction.fee_pct,
            transaction.exchange_rate,
        )

        cursor.execute(command, args)
        connection.commit()

        cursor.close()
        connection.close()

    @staticmethod
    def __get_wallet_id(cursor: Cursor, wallet_address: str) -> int:
        command = """SELECT id
                     FROM wallets
                     WHERE address = ?;"""
        args = (wallet_address,)

        cursor.execute(command, args)
        row = cursor.fetchone()

        return int(row[0])

    def get_user_transactions(self, user: UserInfo) -> List[Transaction]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT w1.address,
                            w2.address,
                            t.amount_in_btc,
                            t.fee_pct,
                            t.btc_usd_exchange_rate
                     FROM transactions t
                     JOIN wallets w1
                     ON t.wallet_id_from = w1.id
                     JOIN wallets w2
                     ON t.wallet_id_to = w2.id
                     JOIN users_wallets uw1
                     ON w1.id = uw1.wallet_id
                     JOIN users_wallets uw2
                     ON w2.id = uw2.wallet_id
                     JOIN users u1
                     ON uw1.user_id = u1.id
                     JOIN users u2
                     ON uw2.user_id = u2.id
                     WHERE u1.api_key = ?
                     OR u2.api_key = ?;"""
        args = (user.api_key, user.api_key)

        cursor.execute(command, args)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        transactions = []

        if rows:
            for row in rows:
                transactions.append(
                    Transaction(
                        wallet_address_from=row[0],
                        wallet_address_to=row[1],
                        btc_amount=row[2],
                        fee_pct=row[3],
                        exchange_rate=row[4],
                    )
                )

        return transactions

    def get_wallet_user(self, wallet: Wallet) -> UserInfo:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT u.email,
                            u.api_key
                     FROM wallets w
                     JOIN users_wallets uw
                     ON w.id = uw.wallet_id
                     JOIN users u
                     ON uw.user_id = u.id
                     WHERE w.address = ?;"""
        args = (wallet.wallet_address,)

        cursor.execute(command, args)
        row = cursor.fetchone()

        cursor.close()
        connection.close()

        return UserInfo(email=row[0], api_key=row[1])

    def add_wallet(self, wallet: Wallet, user: UserInfo) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """INSERT INTO wallets (address, balance_in_btc)
                     VALUES (?, ?);"""
        args = (wallet.wallet_address, wallet.btc_balance)

        cursor.execute(command, args)
        connection.commit()

        user_id = self.__get_user_id(cursor=cursor, api_key=user.api_key)
        wallet_id = self.__get_wallet_id(
            cursor=cursor, wallet_address=wallet.wallet_address
        )

        command = """INSERT INTO users_wallets (user_id, wallet_id)
                     VALUES (?, ?);"""
        new_args = (user_id, wallet_id)

        cursor.execute(command, new_args)
        connection.commit()

        cursor.close()
        connection.close()

    @staticmethod
    def __get_user_id(cursor: Cursor, api_key: str) -> int:
        command = """SELECT id
                     FROM users
                     WHERE api_key = ?;"""
        args = (api_key,)

        cursor.execute(command, args)
        row = cursor.fetchone()

        return int(row[0])

    def get_wallet(self, wallet_address: str) -> Optional[Wallet]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT address,
                            balance_in_btc
                     FROM wallets
                     WHERE address = ?;"""
        args = (wallet_address,)

        cursor.execute(command, args)
        row = cursor.fetchone()

        cursor.close()
        connection.close()
        if row:
            return Wallet(wallet_address=row[0], btc_balance=row[1])
        return None

    def get_wallet_transactions(self, wallet_address: str) -> List[Transaction]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT w1.address,
                            w2.address,
                            t.amount_in_btc,
                            t.fee_pct,
                            t.btc_usd_exchange_rate
                     FROM transactions t
                     JOIN wallets w1
                     ON t.wallet_id_from = w1.id
                     JOIN wallets w2
                     ON t.wallet_id_to = w2.id
                     WHERE w1.address = ?
                     OR w2.address = ?;"""
        args = (wallet_address, wallet_address)

        cursor.execute(command, args)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        transactions = []

        if rows:
            for row in rows:
                transactions.append(
                    Transaction(
                        wallet_address_from=row[0],
                        wallet_address_to=row[1],
                        btc_amount=row[2],
                        fee_pct=row[3],
                        exchange_rate=row[4],
                    )
                )

        return transactions

    def update_wallet_balance(
        self, wallet_address: str, new_btc_balance: float
    ) -> None:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """UPDATE wallets
                     SET balance_in_btc = ?
                     WHERE address = ?;"""
        args = (new_btc_balance, wallet_address)

        cursor.execute(command, args)
        connection.commit()

        cursor.close()
        connection.close()

    def get_user(self, api_key: str) -> Optional[UserInfo]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT api_key,
                            email
                     FROM users
                     WHERE api_key = ?;"""
        args = (api_key,)

        cursor.execute(command, args)
        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if row:
            return UserInfo(api_key=row[0], email=row[1])

        return None

    def get_user_by_email(self, email: str) -> Optional[UserInfo]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT api_key,
                            email
                     FROM users
                     WHERE email = ?;"""
        args = (email,)

        cursor.execute(command, args)
        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if row:
            return UserInfo(api_key=row[0], email=row[1])

        return None

    def get_user_wallets(self, user: UserInfo) -> List[Wallet]:
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()

        command = """SELECT w.address,
                            w.balance_in_btc
                     FROM wallets w
                     JOIN users_wallets uw
                     ON w.id = uw.wallet_id
                     JOIN users u
                     ON uw.user_id = u.id
                     WHERE u.api_key = ?;"""
        args = (user.api_key,)

        cursor.execute(command, args)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        wallets = []

        if rows:
            for row in rows:
                wallets.append(
                    Wallet(
                        wallet_address=row[0],
                        btc_balance=row[1],
                    )
                )

        return wallets
