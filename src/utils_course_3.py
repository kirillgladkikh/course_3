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

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE employers (
                employer_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                id INTEGER
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INTEGER,
                FOREIGN KEY (employer_id) REFERENCES employers(employer_id),
                name VARCHAR(255) NOT NULL,
                salary_from VARCHAR(10) NOT NULL,
                salary_to VARCHAR(10) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                url VARCHAR(255) NOT NULL,
                description TEXT
            )
        """)
        #                 employer_id INT REFERENCE employers(employer_id),

    conn.commit()
    conn.close()



def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """ """
    pass


