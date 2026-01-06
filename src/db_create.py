import psycopg2
from typing import Any


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
                id VARCHAR(50) NOT NULL
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INTEGER,
                FOREIGN KEY (employer_id) REFERENCES employers(employer_id),
                name VARCHAR(255) NOT NULL,
                id VARCHAR(50) NOT NULL,
                salary_from VARCHAR(10) NOT NULL,
                salary_to VARCHAR(10) NOT NULL,
                currency VARCHAR(3) NOT NULL,
                url VARCHAR(255) NOT NULL,
                description TEXT
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """ """
    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for employer=channel in data:
            employer_data=channel_data = employer=channel['employers']  # СДЕЛАТЬ СТРУКТУРУ =============
            cur.execute(
                """
                INSERT INTO employers=channels (name, id)
                VALUES (%s, %s)
                RETURNING employer_id=channel_id
                """,
                (employer_data['name'], employer_data['id'])
            )
            employer_id=channel_id = cur.fetchone()[0]
            vacancies_data=videos_data = employer=channel['vacancies']  # СДЕЛАТЬ СТРУКТУРУ =============
            for vacancy=video in vacancies_data=videos_data:
                vacancy_data=video_data = vacancy=video['???snippet???']  # ??????? НАДО ЛИ ЭТО ВЛОЖЕНИЕ МНЕ ????????
                cur.execute(
                    """
                    INSERT INTO vacancies (employer_id=channel_id, name, id, salary_from, salary_to, currency, url, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        employer_id=channel_id,  # ОСТАВИТЬ employer_id
                        vacancy['name'],
                        vacancy['id'],
                        vacancy['salary']['salary_from'],
                        vacancy['salary']['salary_to'],
                        vacancy['salary']['currency'],
                        vacancy['url'],
                        vacancy['description']
                    )
                )

    conn.commit()
    conn.close()

    # with conn.cursor() as cur:
    #     for employer in data:
    #         employer_data = employer['employer']
    #         # employer_stats = channel['employer']['statistics']
    #         cur.execute(
    #             """
    #             INSERT INTO employers (name, id)
    #             VALUES (%s, %s)
    #             RETURNING employer_id
    #             """,
    #             (
    #                 employer_data['name'],
    #                 employer_data['id']
    #                 # channel_stats['subscriberCount'],
    #                 # channel_stats['videoCount'],
    #                 # f"https://www.youtube.com/channel/{channel['channel']['id']}"
    #             )
    #         )
    #
    #         # """
    #         # INSERT INTO employers (title, views, subscribers, videos, channel_url)
    #         # VALUES (%s, %s, %s, %s, %s)
    #         # RETURNING channel_id
    #         # """,
    #         # (
    #         #     channel_data['title'],
    #         #     channel_stats['viewCount'],
    #         #     channel_stats['subscriberCount'],
    #         #     channel_stats['videoCount'],
    #         #     f"https://www.youtube.com/channel/{channel['channel']['id']}"
    #         # )
    #
    #
    #         employer_id = cur.fetchone()[0]
    #         videos_data = channel['vacancies']
    #
    #         for vacancy in videos_data:
    #             video_data = channel['videos']['snippet']
    #             cur.execute(
    #                 """
    #                 INSERT INTO videos (channel_id, title, publish_date, video_url)
    #                 VALUES (%s, %s, %s, %s)
    #                 """,
    #                 (employer_id, video_data['title'], video_data['publishedAt'],
    #                  f"https://www.youtube.com/watch?v={video['id']['videoId']}")
    #             )
    #
    #
    #             #     """
    #             #     INSERT INTO videos (channel_id, title, publish_date, video_url)
    #             #     VALUES (%s, %s, %s, %s)
    #             #     """,
    #             #     (channel_id, video_data['title'], video_data['publishedAt'],
    #             #      f"https://www.youtube.com/watch?v={video['id']['videoId']}")
    #             # )
    #
    # conn.commit()
    # conn.close()