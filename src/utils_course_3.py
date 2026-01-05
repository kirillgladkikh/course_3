import psycopg2
from typing import Any


def get_hh_data(employers_ids: list[str]) -> list[dict[str, Any]]:
    """ """
    pass


def create_database(database_name: str, params: dict) -> None:
    """ """
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f'DROP DATABASE IF EXISTS {database_name}')
    cur.execute(f'CREATE DATABASE {database_name}')

    cur.close()
    conn.close()


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """ """
    pass


