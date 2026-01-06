import pytest
from unittest.mock import MagicMock, patch
from src.db_manager import DBManager


@pytest.fixture
def db_manager():
    """Фикстура: создаёт экземпляр DBManager с моковым соединением."""
    with patch("psycopg2.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        manager = DBManager("test_db", {"user": "u", "password": "p", "host": "h", "port": 5432})
        manager.conn = mock_conn  # сразу присваиваем моковое соединение
        return manager


def test_get_companies_and_vacancies_count_success(db_manager):
    """Тест: успешный возврат списка компаний с количеством вакансий."""
    # Мокируем курсор и результат запроса
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Имитируем результат SQL-запроса
    mock_cur.__enter__.return_value.fetchall.return_value = [
        ("Company A", 5),
        ("Company B", 0),
        ("Company C", 3),
    ]

    result = db_manager.get_companies_and_vacancies_count()

    # Проверяем структуру и содержимое
    assert isinstance(result, list)
    assert len(result) == 3

    expected = [
        {"company_name": "Company A", "vacancies_count": 5},
        {"company_name": "Company B", "vacancies_count": 0},
        {"company_name": "Company C", "vacancies_count": 3},
    ]
    assert result == expected

    # Проверяем, что запрос выполнен
    assert mock_cur.__enter__.return_value.execute.called


def test_get_companies_and_vacancies_count_empty_result(db_manager):
    """Тест: запрос возвращает пустой результат (нет компаний)."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    mock_cur.__enter__.return_value.fetchall.return_value = []

    result = db_manager.get_companies_and_vacancies_count()

    assert isinstance(result, list)
    assert len(result) == 0

    # Запрос всё равно должен быть выполнен
    assert mock_cur.__enter__.return_value.execute.called


def test_get_companies_and_vacancies_count_auto_connect(db_manager):
    """Тест: метод автоматически устанавливает соединение, если его нет."""
    # Симулируем отсутствие соединения
    db_manager.conn = None

    mock_conn = MagicMock()
    with patch("psycopg2.connect", return_value=mock_conn):
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        mock_cur.__enter__.return_value.fetchall.return_value = [("Single Co", 1)]

        result = db_manager.get_companies_and_vacancies_count()

        assert len(result) == 1
        assert result[0]["company_name"] == "Single Co"
        assert result[0]["vacancies_count"] == 1

        # Проверяем, что connect был вызван
        assert db_manager.conn is mock_conn


def test_get_companies_and_vacancies_count_query_structure(db_manager):
    """Тест: проверяем, что выполняется корректный SQL-запрос."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Не возвращаем данные — только проверяем запрос
    db_manager.get_companies_and_vacancies_count()

    # Получаем выполненный SQL
    executed_sql = mock_cur.__enter__.return_value.execute.call_args[0][0]

    # Проверяем ключевые части запроса
    assert "SELECT" in executed_sql
    assert "e.name AS company_name" in executed_sql
    assert "COUNT(v.vacancy_id) AS vacancies_count" in executed_sql
    assert "FROM employers e" in executed_sql
    assert "LEFT JOIN vacancies v" in executed_sql
    assert "GROUP BY e.employer_id, e.name" in executed_sql
    assert "ORDER BY vacancies_count DESC" in executed_sql


def test_get_companies_and_vacancies_count_exception_handling(db_manager):
    """Тест: обработка исключения при выполнении запроса."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Имитируем ошибку БД
    mock_cur.__enter__.return_value.execute.side_effect = Exception("DB error")

    with pytest.raises(Exception) as exc_info:
        db_manager.get_companies_and_vacancies_count()

    assert "DB error" in str(exc_info.value)


def test_get_all_vacancies_success(db_manager):
    """Тест: успешный возврат списка всех вакансий."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Имитируем результат SQL-запроса
    mock_cur.__enter__.return_value.fetchall.return_value = [
        ("Company A", "Dev", 100000, 150000, "RUB", "http://job.ru/1"),
        ("Company B", "QA", 80000, 120000, "USD", "http://job.ru/2"),
    ]

    result = db_manager.get_all_vacancies()

    # Проверяем структуру и содержимое
    assert isinstance(result, list)
    assert len(result) == 2

    expected = [
        {
            "company_name": "Company A",
            "vacancy_name": "Dev",
            "salary_from": 100000,
            "salary_to": 150000,
            "currency": "RUB",
            "url": "http://job.ru/1",
        },
        {
            "company_name": "Company B",
            "vacancy_name": "QA",
            "salary_from": 80000,
            "salary_to": 120000,
            "currency": "USD",
            "url": "http://job.ru/2",
        },
    ]
    assert result == expected

    # Проверяем, что запрос выполнен
    assert mock_cur.__enter__.return_value.execute.called


def test_get_all_vacancies_empty_result(db_manager):
    """Тест: запрос возвращает пустой результат (нет вакансий)."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    mock_cur.__enter__.return_value.fetchall.return_value = []

    result = db_manager.get_all_vacancies()

    assert isinstance(result, list)
    assert len(result) == 0

    # Запрос всё равно должен быть выполнен
    assert mock_cur.__enter__.return_value.execute.called


def test_get_all_vacancies_auto_connect(db_manager):
    """Тест: метод автоматически устанавливает соединение, если его нет."""
    # Симулируем отсутствие соединения
    db_manager.conn = None

    mock_conn = MagicMock()
    with patch("psycopg2.connect", return_value=mock_conn):
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        mock_cur.__enter__.return_value.fetchall.return_value = [
            ("Solo Co", "Lead", 200000, 300000, "EUR", "http://job.ru/3")
        ]

        result = db_manager.get_all_vacancies()

        assert len(result) == 1
        assert result[0]["company_name"] == "Solo Co"
        assert result[0]["vacancy_name"] == "Lead"

        # Проверяем, что connect был вызван
        assert db_manager.conn is mock_conn


def test_get_all_vacancies_query_structure(db_manager):
    """Тест: проверяем, что выполняется корректный SQL-запрос."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Не возвращаем данные — только проверяем запрос
    db_manager.get_all_vacancies()

    # Получаем выполненный SQL
    executed_sql = mock_cur.__enter__.return_value.execute.call_args[0][0]

    # Проверяем ключевые части запроса
    assert "SELECT" in executed_sql
    assert "e.name" in executed_sql
    assert "v.name" in executed_sql
    assert "v.salary_from" in executed_sql
    assert "v.salary_to" in executed_sql
    assert "v.currency" in executed_sql
    assert "v.url" in executed_sql
    assert "FROM vacancies v" in executed_sql
    assert "JOIN employers e ON v.employer_id = e.employer_id" in executed_sql


def test_get_all_vacancies_exception_handling(db_manager):
    """Тест: обработка исключения при выполнении запроса."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Имитируем ошибку БД
    mock_cur.__enter__.return_value.execute.side_effect = Exception("DB query failed")

    with pytest.raises(Exception) as exc_info:
        db_manager.get_all_vacancies()

    assert "DB query failed" in str(exc_info.value)


def test_get_avg_salary_success(db_manager):
    """Тест: успешный расчёт средней зарплаты."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Имитируем результат SQL-запроса: средняя зарплата = 125000
    mock_cur.__enter__.return_value.fetchone.return_value = (125000.0,)

    result = db_manager.get_avg_salary()

    assert isinstance(result, float)
    assert result == 125000.0

    # Проверяем, что запрос выполнен
    assert mock_cur.__enter__.return_value.execute.called


def test_get_avg_salary_no_vacancies(db_manager):
    """Тест: в БД нет вакансий → средняя зарплата = 0.0."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # SQL возвращает NULL (нет записей)
    mock_cur.__enter__.return_value.fetchone.return_value = (None,)

    result = db_manager.get_avg_salary()

    assert isinstance(result, float)
    assert result == 0.0

    # Запрос выполнен
    assert mock_cur.__enter__.return_value.execute.called


def test_get_avg_salary_auto_connect(db_manager):
    """Тест: метод автоматически устанавливает соединение, если его нет."""
    # Симулируем отсутствие соединения
    db_manager.conn = None

    mock_conn = MagicMock()
    with patch("psycopg2.connect", return_value=mock_conn):
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        # Возвращаем среднее = 90000
        mock_cur.__enter__.return_value.fetchone.return_value = (90000.0,)

        result = db_manager.get_avg_salary()

        assert result == 90000.0

        # Проверяем, что connect был вызван
        assert db_manager.conn is mock_conn


def test_get_avg_salary_query_structure(db_manager):
    """Тест: проверяем, что выполняется корректный SQL-запрос."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Не возвращаем данные — только проверяем запрос
    db_manager.get_avg_salary()

    # Получаем выполненный SQL
    executed_sql = mock_cur.__enter__.return_value.execute.call_args[0][0]

    # Проверяем ключевые части запроса
    assert "SELECT AVG" in executed_sql
    assert "(NULLIF(salary_from, '0')::numeric + NULLIF(salary_to, '0')::numeric) / 2" in executed_sql
    assert "FROM vacancies" in executed_sql

    assert "::numeric" in executed_sql  # приведение типов


def test_get_avg_salary_exception_handling(db_manager):
    """Тест: обработка исключения при выполнении запроса."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Имитируем ошибку БД
    mock_cur.__enter__.return_value.execute.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        db_manager.get_avg_salary()

    assert "Database error" in str(exc_info.value)


def test_get_vacancies_with_higher_salary_success(db_manager):
    """Тест: успешный возврат вакансий с зарплатой выше средней."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    # Мокируем среднюю зарплату (результат get_avg_salary)
    with patch.object(db_manager, "get_avg_salary", return_value=100000.0):
        # Результат SQL-запроса: 2 вакансии с зарплатой > 100000
        mock_cur.__enter__.return_value.fetchall.return_value = [
            ("Company A", "Dev", 120000, 150000, "RUB", "http://job.ru/1"),
            ("Company B", "Lead", 110000, 130000, "USD", "http://job.ru/2"),
        ]

        result = db_manager.get_vacancies_with_higher_salary()

        assert isinstance(result, list)
        assert len(result) == 2

        expected = [
            {
                "company_name": "Company A",
                "vacancy_name": "Dev",
                "salary_from": 120000,
                "salary_to": 150000,
                "currency": "RUB",
                "url": "http://job.ru/1",
            },
            {
                "company_name": "Company B",
                "vacancy_name": "Lead",
                "salary_from": 110000,
                "salary_to": 130000,
                "currency": "USD",
                "url": "http://job.ru/2",
            },
        ]
        assert result == expected

        # Проверяем, что запрос выполнен
        assert mock_cur.__enter__.return_value.execute.called


def test_get_vacancies_with_higher_salary_empty_result(db_manager):
    """Тест: нет вакансий с зарплатой выше средней → пустой список."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    with patch.object(db_manager, "get_avg_salary", return_value=200000.0):
        mock_cur.__enter__.return_value.fetchall.return_value = []

        result = db_manager.get_vacancies_with_higher_salary()

        assert isinstance(result, list)
        assert len(result) == 0

        # Запрос выполнен
        assert mock_cur.__enter__.return_value.execute.called


def test_get_vacancies_with_higher_salary_auto_connect(db_manager):
    """Тест: метод автоматически устанавливает соединение, если его нет."""
    db_manager.conn = None  # нет соединения

    mock_conn = MagicMock()
    with patch("psycopg2.connect", return_value=mock_conn):
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        with patch.object(db_manager, "get_avg_salary", return_value=80000.0):
            mock_cur.__enter__.return_value.fetchall.return_value = [
                ("Solo Co", "QA", 90000, 100000, "EUR", "http://job.ru/3")
            ]

            result = db_manager.get_vacancies_with_higher_salary()

            assert len(result) == 1
            assert result[0]["company_name"] == "Solo Co"

            # Проверяем, что connect был вызван
            assert db_manager.conn is mock_conn


def test_get_vacancies_with_higher_salary_query_params(db_manager):
    """Тест: проверка передачи параметра (средней зарплаты) в SQL-запрос."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    with patch.object(db_manager, "get_avg_salary", return_value=75000.0):
        db_manager.get_vacancies_with_higher_salary()

        # Получаем аргументы вызова execute
        executed_sql, param = mock_cur.__enter__.return_value.execute.call_args[0]

        # Проверяем SQL
        assert (
            "WHERE ((NULLIF(v.salary_from, '0')::numeric + NULLIF(v.salary_to, '0')::numeric) / 2) > %s"
            in executed_sql
        )
        # Проверяем параметр
        assert param == (75000.0,)


def test_get_vacancies_with_higher_salary_query_structure(db_manager):
    """Тест: проверяем структуру SQL-запроса."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    with patch.object(db_manager, "get_avg_salary", return_value=50000.0):
        db_manager.get_vacancies_with_higher_salary()

    executed_sql = mock_cur.__enter__.return_value.execute.call_args[0][0]

    # Проверяем ключевые части запроса по отдельности
    assert "SELECT e.name, v.name" in executed_sql
    assert "v.salary_from" in executed_sql
    assert "v.salary_to" in executed_sql
    assert "v.currency" in executed_sql
    assert "v.url" in executed_sql

    assert "FROM vacancies v" in executed_sql
    assert "JOIN employers e" in executed_sql
    assert "ON v.employer_id = e.employer_id" in executed_sql

    assert (
        "WHERE ((NULLIF(v.salary_from, '0')::numeric + " "NULLIF(v.salary_to, '0')::numeric) / 2) > %s"
    ) in executed_sql


def test_get_vacancies_with_higher_salary_exception_handling(db_manager):
    """Тест: обработка исключения при выполнении запроса."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    with patch.object(db_manager, "get_avg_salary", return_value=60000.0):
        mock_cur.__enter__.return_value.execute.side_effect = Exception("Query failed")

        with pytest.raises(Exception) as exc_info:
            db_manager.get_vacancies_with_higher_salary()

        assert "Query failed" in str(exc_info.value)


def test_get_vacancies_with_keyword_success(db_manager):
    """Тест: успешный поиск вакансий по ключевому слову."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    keyword = "python"
    mock_cur.__enter__.return_value.fetchall.return_value = [
        ("Company A", "Python Dev", 120000, 150000, "RUB", "http://job.ru/1"),
        ("Company B", "Senior Python Engineer", 180000, 220000, "USD", "http://job.ru/2"),
    ]

    result = db_manager.get_vacancies_with_keyword(keyword)

    assert isinstance(result, list)
    assert len(result) == 2

    expected = [
        {
            "company_name": "Company A",
            "vacancy_name": "Python Dev",
            "salary_from": 120000,
            "salary_to": 150000,
            "currency": "RUB",
            "url": "http://job.ru/1",
        },
        {
            "company_name": "Company B",
            "vacancy_name": "Senior Python Engineer",
            "salary_from": 180000,
            "salary_to": 220000,
            "currency": "USD",
            "url": "http://job.ru/2",
        },
    ]
    assert result == expected

    assert mock_cur.__enter__.return_value.execute.called


def test_get_vacancies_with_keyword_empty_result(db_manager):
    """Тест: нет вакансий с указанным ключевым словом → пустой список."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    keyword = "golang"
    mock_cur.__enter__.return_value.fetchall.return_value = []

    result = db_manager.get_vacancies_with_keyword(keyword)

    assert isinstance(result, list)
    assert len(result) == 0
    assert mock_cur.__enter__.return_value.execute.called


def test_get_vacancies_with_keyword_auto_connect(db_manager):
    """Тест: метод автоматически устанавливает соединение, если его нет."""
    db_manager.conn = None  # нет соединения

    mock_conn = MagicMock()
    with patch("psycopg2.connect", return_value=mock_conn):
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur

        keyword = "java"
        mock_cur.__enter__.return_value.fetchall.return_value = [
            ("Solo Co", "Java Backend", 150000, 180000, "EUR", "http://job.ru/3")
        ]

        result = db_manager.get_vacancies_with_keyword(keyword)

        assert len(result) == 1
        assert result[0]["vacancy_name"] == "Java Backend"

        # Проверяем, что connect был вызван
        assert db_manager.conn is mock_conn


def test_get_vacancies_with_keyword_query_params(db_manager):
    """Тест: проверка передачи параметра (ключевого слова) в SQL-запрос."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    keyword = "react"
    db_manager.get_vacancies_with_keyword(keyword)

    # Получаем аргументы вызова execute
    executed_sql, param = mock_cur.__enter__.return_value.execute.call_args[0]

    # Проверяем SQL
    assert "WHERE v.name ILIKE %s" in executed_sql
    # Проверяем параметр (должен быть с % по краям)
    assert param == (f"%{keyword}%",)


def test_get_vacancies_with_keyword_query_structure(db_manager):
    """Тест: проверяем структуру SQL-запроса."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    keyword = "js"
    db_manager.get_vacancies_with_keyword(keyword)

    executed_sql = mock_cur.__enter__.return_value.execute.call_args[0][0]

    # Проверяем наличие всех выбираемых полей
    assert "SELECT e.name, v.name" in executed_sql
    assert "v.salary_from" in executed_sql
    assert "v.salary_to" in executed_sql
    assert "v.currency" in executed_sql
    assert "v.url" in executed_sql

    # Проверяем части FROM и JOIN по отдельности
    assert "FROM vacancies v" in executed_sql
    assert "JOIN employers e" in executed_sql
    assert "ON v.employer_id = e.employer_id" in executed_sql

    # Проверяем условие WHERE
    assert "WHERE v.name ILIKE %s" in executed_sql


def test_get_vacancies_with_keyword_exception_handling(db_manager):
    """Тест: обработка исключения при выполнении запроса."""
    mock_cur = MagicMock()
    db_manager.conn.cursor.return_value = mock_cur

    keyword = "rust"
    mock_cur.__enter__.return_value.execute.side_effect = Exception("Database query error")

    with pytest.raises(Exception) as exc_info:
        db_manager.get_vacancies_with_keyword(keyword)

    assert "Database query error" in str(exc_info.value)
