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
                currency VARCHAR(5) NOT NULL,
                url VARCHAR(255) NOT NULL,
                description TEXT
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(data: dict[str, Any], database_name: str, params: dict) -> None:
    """Сохраняет данные о работодателях и вакансиях в БД."""
    conn = psycopg2.connect(dbname=database_name, **params)

    try:
        with conn.cursor() as cur:
            # 1. Сохраняем работодателей
            employers_data = data["employers"]
            for employer in employers_data:
                cur.execute(
                    """
                    INSERT INTO employers (name, id)
                    VALUES (%s, %s)
                    RETURNING employer_id
                    """,
                    (employer["name"], employer["id"])
                )
                employer_id = cur.fetchone()[0]  # Получаем ID добавленного работодателя

                # 2. Сохраняем вакансии этого работодателя
                # (если нужно связать вакансии с конкретным работодателем по ID)
                # Но в вашем случае вакансии уже содержат employer_info → см. ниже

            # 3. Сохраняем все вакансии (они уже содержат ссылку на работодателя)
            vacancies_data = data["vacancies"]
            for vacancy in vacancies_data:
                # Извлекаем данные о работодателе из вакансии
                emp_info = vacancy["employer"]
                if emp_info:
                    # Ищем employer_id по id работодателя
                    cur.execute(
                        "SELECT employer_id FROM employers WHERE id = %s",
                        (emp_info["id"],)
                    )
                    result = cur.fetchone()
                    if result:
                        employer_id = result[0]
                    else:
                        # Если работодатель не найден — пропускаем или добавляем
                        print(f"Работодатель с id={emp_info['id']} не найден в БД")
                        continue
                else:
                    employer_id = None  # Вакансия без указания работодателя

                cur.execute(
                    """
                    INSERT INTO vacancies 
                    (employer_id, name, id, salary_from, salary_to, currency, url, description)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        employer_id,
                        vacancy["name"],
                        vacancy["id"],
                        vacancy["salary"]["from"],
                        vacancy["salary"]["to"],
                        vacancy["salary"]["currency"],
                        vacancy["url"],
                        vacancy["description"]
                    )
                )

        conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении данных в БД: {e}")
        conn.rollback()
    finally:
        conn.close()


# def save_data_to_database(data: dict[str, Any], database_name: str, params: dict) -> None:
#     """ """
#     conn = psycopg2.connect(dbname=database_name, **params)
#
#     with conn.cursor() as cur:
#         for employer in data:
#             employer_data = employer['employers']  # СДЕЛАТЬ СТРУКТУРУ =============
#             cur.execute(
#                 """
#                 INSERT INTO employers=channels (name, id)
#                 VALUES (%s, %s)
#                 RETURNING employer_id=channel_id
#                 """,
#                 (employer_data['name'], employer_data['id'])
#             )
#             employer_id = cur.fetchone()[0]
#             vacancies_data = employer['vacancies']  # СДЕЛАТЬ СТРУКТУРУ =============
#             for vacancy in vacancies_data:
#                 # vacancy_data = vacancy['???snippet???']  # ??????? НАДО ЛИ ЭТО ВЛОЖЕНИЕ МНЕ ????????
#                 cur.execute(
#                     """
#                     INSERT INTO vacancies (employer_id, name, id, salary_from, salary_to, currency, url, description)
#                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                     """,
#                     (
#                         employer_id,  # ОСТАВИТЬ employer_id
#                         vacancy['name'],
#                         vacancy['id'],
#                         vacancy['salary']['salary_from'],
#                         vacancy['salary']['salary_to'],
#                         vacancy['salary']['currency'],
#                         vacancy['url'],
#                         vacancy['description']
#                     )
#                 )
#
#     conn.commit()
#     conn.close()

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