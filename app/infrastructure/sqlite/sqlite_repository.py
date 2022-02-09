import sqlite3


class SQLiteRepository:
    def __init__(self, db_name: str = "bitcoin_wallet.db") -> None:
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
