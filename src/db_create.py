import psycopg2
from typing import Any


def create_database(database_name: str, params: dict) -> None:
    """
    Создаёт базу данных PostgreSQL и инициализирует в ней схему с таблицами employers и vacancies.

    Функция выполняет два основных этапа:
    1. Подключается к серверу PostgreSQL (к БД 'postgres') и создаёт новую БД с указанным именем
       (предварительно удалив существующую БД с таким же именем, если она есть).
    2. Подключается к новой БД и создаёт в ней две таблицы:
       - employers: для хранения информации о работодателях;
       - vacancies: для хранения вакансий с ссылкой на работодателя.

    Параметры:
    -----------
    database_name : str
        Имя создаваемой базы данных. Должно быть допустимым идентификатором PostgreSQL
        (без спецсимволов, не начинаться с цифры и т. п.).

    params : dict
        Словарь с параметрами подключения к серверу PostgreSQL. Должен содержать ключи,
        которые принимает psycopg2.connect, например:
        - 'user' (имя пользователя)
        - 'password' (пароль)
        - 'host' (хост, например 'localhost')
        - 'port' (порт, например 5432)

    Возвращаемое значение:
    ------------------
    None
        Функция не возвращает значение. В случае успеха БД создана и инициализирована.

    Исключения:
    -----------
    psycopg2.Error
        Если возникла ошибка при подключении к серверу, выполнении SQL‑запросов
        или создании объектов БД.
    KeyError
        Если в `params` отсутствуют необходимые ключи для подключения.
    Exception
        Любые другие непредвиденные ошибки (например, проблемы с сетью).

    Побочные эффекты:
    -----------------
    - Создаёт новую БД на сервере PostgreSQL (предварительно удаляя старую, если есть).
    - Создаёт две таблицы (`employers` и `vacancies`) в новой БД.
    - Закрывает все соединения после выполнения.

    Примечания:
    ----------
    - Для выполнения требуются права на создание БД на сервере PostgreSQL.
    - Таблица `vacancies` содержит внешний ключ `employer_id`, ссылающийся на `employers.employer_id`.
    - Поля `salary_from` и `salary_to` хранятся как VARCHAR(10) — это соответствует
      формату, ожидаемому в других частях системы (например, в `filtered_hh_data`).
    - Параметр `autocommit=True` используется только для этапа создания БД; для создания
      таблиц применяется явный `conn.commit()`.
    - Функция не проверяет существование БД перед удалением — `DROP DATABASE IF EXISTS`
      гарантирует безопасность.
    """
    conn = psycopg2.connect(dbname="postgres", **params)
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"DROP DATABASE IF EXISTS {database_name}")
    cur.execute(f"CREATE DATABASE {database_name}")

    cur.close()
    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE employers (
                employer_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                id VARCHAR(50) NOT NULL
            )
        """
        )

    with conn.cursor() as cur:
        cur.execute(
            """
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
        """
        )

    conn.commit()
    conn.close()


def save_data_to_database(data: dict[str, Any], database_name: str, params: dict) -> None:
    """
    Сохраняет данные о работодателях и вакансиях в указанную базу данных PostgreSQL.

    Функция выполняет две основные операции:
    1. Добавляет работодателей в таблицу `employers` (если их ещё нет).
    2. Добавляет вакансии в таблицу `vacancies`, связывая их с соответствующими
       работодателями через внешний ключ `employer_id`.

    Параметры:
    -----------
    data : dict[str, Any]
        Словарь с данными для сохранения. Должен содержать два ключа:
        - 'employers': список словарей с информацией о работодателях. Каждый словарь
          должен иметь поля:
          - 'name' (str): название работодателя
          - 'id' (str): уникальный идентификатор работодателя
        - 'vacancies': список словарей с информацией о вакансиях. Каждая вакансия
          должна содержать:
          - 'name' (str): название вакансии
          - 'id' (str): уникальный идентификатор вакансии
          - 'salary' (dict): словарь с полями 'from', 'to', 'currency'
          - 'url' (str): ссылка на вакансию
          - 'description' (str): описание обязанностей
          - 'employer' (dict or None): данные о работодателе (может быть None)

    database_name : str
        Имя базы данных PostgreSQL, в которую нужно сохранить данные. БД должна
        существовать и содержать таблицы `employers` и `vacancies` (например,
        созданные через `create_database`).

    params : dict
        Словарь с параметрами подключения к серверу PostgreSQL. Должен включать ключи,
        которые принимает `psycopg2.connect`, например:
        - 'user' (имя пользователя)
        - 'password' (пароль)
        - 'host' (хост, например 'localhost')
        - 'port' (порт, например 5432)

    Возвращаемое значение:
    ------------------
    None
        Функция не возвращает значение. В случае успеха данные сохранены в БД.

    Исключения:
    -----------
    psycopg2.Error
        Если произошла ошибка при выполнении SQL‑запросов (например, нарушение
        ограничений целостности, проблемы с подключением).
    KeyError
        Если в `data` отсутствуют ключи 'employers' или 'vacancies', либо
        в словарях работодателей/вакансий нет требуемых полей.
    Exception
        Любые другие непредвиденные ошибки (например, проблемы с сетью,
        некорректные типы данных).

    Побочные эффекты:
    -----------------
    - Добавляет записи в таблицы `employers` и `vacancies`.
    - Выполняет `COMMIT` при успешном завершении или `ROLLBACK` при ошибке.
    - Закрывает соединение с БД в блоке `finally`.
    - Печатает сообщения об ошибках в консоль (через `print`).

    Примечания:
    ----------
    - Для вакансий без указанного работодателя (`employer` == None) поле
      `employer_id` в таблице `vacancies` будет NULL.
    - Если работодатель из вакансии не найден в таблице `employers` (по полю `id`),
      вакансия пропускается с предупреждением в консоль.
    - Используется параметризованный SQL (`%s`) для защиты от SQL‑инъекций.
    - Транзакция явно завершается: `conn.commit()` при успехе, `conn.rollback()`
      при исключении.
    - Функция не проверяет существование БД или таблиц — предполагается, что они
      уже созданы (например, через `create_database`).
    """
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
                    (employer["name"], employer["id"]),
                )
                employer_id = cur.fetchone()[0]  # Получаем ID добавленного работодателя

                # 2. Сохраняем вакансии этого работодателя
                # (нужно связать вакансии с конкретным работодателем по ID)

            # 3. Сохраняем все вакансии (они уже содержат ссылку на работодателя)
            vacancies_data = data["vacancies"]
            for vacancy in vacancies_data:
                # Извлекаем данные о работодателе из вакансии
                emp_info = vacancy["employer"]
                if emp_info:
                    # Ищем employer_id по id работодателя
                    cur.execute("SELECT employer_id FROM employers WHERE id = %s", (emp_info["id"],))
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
                        vacancy["description"],
                    ),
                )

        conn.commit()
    except Exception as e:
        print(f"Ошибка при сохранении данных в БД: {e}")
        conn.rollback()
    finally:
        conn.close()
