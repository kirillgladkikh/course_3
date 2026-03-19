import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from src.db_create import create_database, save_data_to_database


@patch("psycopg2.connect")
def test_create_database_success(mock_connect):
    """Тест: успешное создание БД и таблиц."""
    # 1. Создаём мок-соединения
    mock_postgres_conn = MagicMock()
    mock_new_db_conn = MagicMock()

    # 2. Настраиваем connect() на возврат соединений
    mock_connect.side_effect = [mock_postgres_conn, mock_new_db_conn]

    # 3. Создаём мок-курсоры
    mock_postgres_cur = MagicMock()
    mock_new_db_cur = MagicMock()

    # 4. Настраиваем cursor() на возврат моков
    mock_postgres_conn.cursor.return_value = mock_postgres_cur
    mock_new_db_conn.cursor.return_value = mock_new_db_cur

    # 5. Настраиваем контекстные менеджеры для курсоров
    mock_postgres_cur.__enter__.return_value = mock_postgres_cur
    mock_new_db_cur.__enter__.return_value = mock_new_db_cur

    # 6. Разрешаем выполнение команд (без ошибок)
    mock_postgres_cur.execute.side_effect = None
    mock_new_db_cur.execute.side_effect = None

    # 7. Вызываем функцию
    params = {"user": "testuser", "password": "testpass", "host": "localhost", "port": 5432}
    create_database("test_db", params)

    # 8. Проверяем вызовы к первому соединению (postgres)
    assert mock_postgres_cur.execute.call_count == 2
    assert "DROP DATABASE IF EXISTS test_db" in str(mock_postgres_cur.execute.call_args_list[0])
    assert "CREATE DATABASE test_db" in str(mock_postgres_cur.execute.call_args_list[1])

    # 9. Проверяем создание таблиц во втором соединении
    assert mock_new_db_cur.execute.call_count == 2
    create_table_employers = mock_new_db_cur.execute.call_args_list[0][0][0]
    create_table_vacancies = mock_new_db_cur.execute.call_args_list[1][0][0]

    assert "CREATE TABLE employers" in create_table_employers
    assert "CREATE TABLE vacancies" in create_table_vacancies

    # 10. Проверяем закрытие соединений
    assert mock_postgres_conn.close.called
    assert mock_new_db_conn.close.called


@patch("psycopg2.connect")
def test_create_database_create_fails(mock_connect):
    """Тест: ошибка при CREATE DATABASE."""
    mock_postgres_conn = MagicMock()
    mock_connect.return_value = mock_postgres_conn

    mock_cur = MagicMock()
    mock_postgres_conn.cursor.return_value = mock_cur

    # Ошибка при CREATE DATABASE
    mock_cur.execute.side_effect = [None, psycopg2.Error("CREATE failed")]

    params = {"user": "test", "password": "pass", "host": "localhost", "port": 5432}

    with pytest.raises(psycopg2.Error, match="CREATE failed"):
        create_database("test_db", params)


def test_create_database_missing_params():
    """Тест: отсутствие обязательных ключей в params (вызывает ошибку psycopg2)."""
    params_missing = {"user": "test", "host": "localhost"}  # нет password и port

    with pytest.raises(psycopg2.OperationalError, match="fe_sendauth: no password supplied"):
        create_database("test_db", params_missing)


@patch("psycopg2.connect")
def test_create_database_connection_fails(mock_connect):
    """Тест: не удаётся подключиться к серверу PostgreSQL."""
    mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

    params = {"user": "test", "password": "pass", "host": "localhost", "port": 5432}

    with pytest.raises(psycopg2.OperationalError, match="Connection failed"):
        create_database("test_db", params)


@patch("psycopg2.connect")
def test_save_data_success(mock_connect):
    """Тест: данные успешно сохранены в БД."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Настраиваем контекстный менеджер для курсора
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__ = MagicMock()

    data = {
        "employers": [
            {"name": "Company A", "id": "101"},
            {"name": "Company B", "id": "102"},
        ],
        "vacancies": [
            {
                "name": "Dev",
                "id": "201",
                "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
                "url": "http://job.ru/1",
                "description": "Code",
                "employer": {"id": "101"},
            }
        ],
    }

    params = {"user": "u", "password": "p", "host": "h", "port": 5432}

    # Вызываем функцию
    save_data_to_database(data, "test_db", params)

    # Отладка: выводим все выполненные SQL-запросы
    print("\n=== ВЫПОЛНЕННЫЕ SQL-ЗАПРОСЫ ===")
    for i, call in enumerate(mock_cur.execute.call_args_list):
        print(f"Запрос {i+1}: {call.args[0]}")

    # Проверяем, что число INSERT соответствует количеству записей
    expected_insert_count = len(data["employers"]) + len(data["vacancies"])
    assert mock_cur.execute.call_count >= expected_insert_count, (
        f"Ожидалось минимум {expected_insert_count} INSERT-запросов, " f"но выполнено {mock_cur.execute.call_count}"
    )

    # Проверяем, что commit вызван ровно один раз (после всех INSERT)
    assert mock_conn.commit.call_count == 1, "commit не был вызван или вызван несколько раз"

    # Проверяем, что rollback НЕ вызван (ошибок не было)
    assert not mock_conn.rollback.called, "rollback был вызван (не должно быть ошибок)"

    # Дополнительно: проверяем, что соединение закрыто
    assert mock_conn.close.call_count == 1, "close не был вызван"


@patch("psycopg2.connect")
def test_vacancy_without_employer(mock_connect):
    """Тест: вакансия без указания работодателя (employer=None)."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Настраиваем контекстный менеджер для курсора
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__ = MagicMock()

    data = {
        "employers": [],
        "vacancies": [
            {
                "name": "Manager",
                "id": "301",
                "salary": {"from": 80000, "to": 120000, "currency": "RUB"},
                "url": "http://job.ru/2",
                "description": "Manage",
                "employer": None,
            }
        ],
    }
    params = {"user": "u", "password": "p", "host": "h", "port": 5432}

    save_data_to_database(data, "test_db", params)

    # Проверяем, что был вызван INSERT INTO vacancies
    assert mock_cur.execute.call_count >= 1

    # Извлекаем аргументы последнего вызова execute()
    last_call = mock_cur.execute.call_args_list[-1]
    sql = last_call[0][0]  # SQL-запрос
    values = last_call[0][1]  # Параметры запроса

    assert "INSERT INTO vacancies" in sql
    assert values[0] is None  # employer_id = None

    # Проверяем commit и закрытие соединения
    assert mock_conn.commit.called
    assert not mock_conn.rollback.called
    assert mock_conn.close.called


@patch("psycopg2.connect")
@patch("builtins.print")
def test_employer_not_found_in_db(mock_print, mock_connect):
    """Тест: работодатель из вакансии не найден в таблице employers."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    # Настраиваем контекстный менеджер для курсора
    mock_cur.__enter__.return_value = mock_cur
    mock_cur.__exit__ = MagicMock()

    # SELECT возвращает None → работодатель не найден
    mock_cur.fetchone.return_value = None

    data = {
        "employers": [],  # в БД нет работодателей
        "vacancies": [
            {
                "name": "QA",
                "id": "401",
                "salary": {"from": 70000, "to": 90000, "currency": "RUB"},
                "url": "http://job.ru/3",
                "description": "Test",
                "employer": {"id": "999"},  # такого id нет в БД
            }
        ],
    }
    params = {"user": "u", "password": "p", "host": "h", "port": 5432}

    save_data_to_database(data, "test_db", params)

    # Проверяем, что сообщение об ошибке выведено
    expected_msg = "Работодатель с id=999 не найден в БД"
    assert any(expected_msg in str(call) for call in mock_print.call_args_list)

    # Проверяем, что INSERT INTO vacancies не выполнен (вакансия пропущена)
    insert_calls = [call for call in mock_cur.execute.call_args_list if "INSERT INTO vacancies" in str(call[0][0])]
    assert len(insert_calls) == 0

    # Проверяем commit (должен быть, т.к. нет исключения)
    assert mock_conn.commit.called
    assert not mock_conn.rollback.called
    assert mock_conn.close.called


@patch("psycopg2.connect")
@patch("builtins.print")
def test_invalid_vacancy_salary_missing_from(mock_print, mock_connect):
    """Тест: в вакансии отсутствует поле salary['from'] — проверяется вывод ошибки и rollback."""
    mock_conn = MagicMock()
    mock_cur = MagicMock()

    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cur

    data = {
        "employers": [{"name": "Company A", "id": "101"}],
        "vacancies": [
            {
                "name": "Dev",
                "id": "201",
                "salary": {"to": 150000, "currency": "RUB"},  # нет 'from'
                "url": "http://job.ru/1",
                "description": "Code",
                "employer": {"id": "101"},
            }
        ],
    }
    params = {"user": "u", "password": "p", "host": "h", "port": 5432}

    # Вызываем функцию (не ждём исключения!)
    save_data_to_database(data, "test_db", params)

    # Проверяем, что было сообщение об ошибке
    assert any("'from'" in str(call) for call in mock_print.call_args_list)

    # Проверяем rollback и закрытие
    assert mock_conn.rollback.called
    assert mock_conn.close.called
    assert not mock_conn.commit.called  # commit не должен быть вызван
