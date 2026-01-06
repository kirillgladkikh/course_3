import pytest
from unittest.mock import patch, MagicMock
from src.hh_data import get_hh_data, filtered_hh_data, get_emp_vac_dict


@patch("src.hh_data.connect")  # заменяем connect на mock
def test_get_hh_data_success(mock_connect):
    """Тест: успешный ответ API с валидным списком вакансий."""
    # Подготавливаем mock-ответ от API
    mock_connect.return_value = {
        "items": [
            {"id": "1", "name": "Dev"},
            {"id": "2", "name": "QA"}
        ]
    }

    employers = [{"id": "1721725", "name": "Rocket10"}]

    result = get_hh_data(employers)

    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert result[1]["name"] == "QA"



@patch("src.hh_data.connect")
def test_get_hh_data_no_items(mock_connect):
    """Тест: ответ API без ключа 'items' или items не список."""
    # Случай 1: нет ключа 'items'
    mock_connect.return_value = {"some_key": "value"}

    employers = [{"id": "1579449", "name": "idaproject"}]
    result = get_hh_data(employers)

    assert len(result) == 0  # данных не добавили

    # Случай 2: items есть, но не список
    mock_connect.return_value = {"items": "not a list"}

    result = get_hh_data(employers)
    assert len(result) == 0



@patch("src.hh_data.connect")
def test_get_hh_data_exception(mock_connect):
    """Тест: исключение при вызове connect (например, сеть упала)."""
    mock_connect.side_effect = Exception("Network error")

    employers = [{"id": "1721725", "name": "Rocket10"}]

    result = get_hh_data(employers)

    assert len(result) == 0  # ошибка → данных нет
    # Дополнительно: можно проверить, что print вызвал сообщение (через capsys)



def test_get_hh_data_empty_employers():
    """Тест: пустой список работодателей."""
    result = get_hh_data([])
    assert len(result) == 0



@patch("src.hh_data.connect")
def test_get_hh_data_multiple_employers(mock_connect):
    """Тест: несколько работодателей — данные объединяются."""
    mock_connect.side_effect = [
        {"items": [{"id": "1", "name": "Job A"}]},      # для первого
        {"items": [{"id": "2", "name": "Job B"}]},      # для второго
        {"items": []},                                   # для третьего — пустой список
    ]

    employers = [
        {"id": "1", "name": "A"},
        {"id": "2", "name": "B"},
        {"id": "3", "name": "C"},
    ]

    result = get_hh_data(employers)

    assert len(result) == 2  # из первых двух по 1 вакансии, третья — пустая
    assert result[0]["name"] == "Job A"
    assert result[1]["id"] == "2"



@patch("src.hh_data.connect")
def test_get_hh_data_items_is_empty_list(mock_connect):
    """Тест: items — пустой список (корректный формат, но нет данных)."""
    mock_connect.return_value = {"items": []}

    employers = [{"id": "123", "name": "EmptyCo"}]
    result = get_hh_data(employers)

    assert len(result) == 0  # нет вакансий, но ошибки нет


def test_filtered_hh_data_full_data():
    """Тест: вакансия со всеми полями (полный набор данных)."""
    input_vacancies = [
        {
            "name": "Python Developer",
            "id": "123",
            "salary": {
                "from": 100000,
                "to": 150000,
                "currency": "RUB"
            },
            "snippet": {
                "responsibility": "Разработка API"
            },
            "employer": {
                "id": "1721725",
                "name": "Rocket10"
            },
            "alternate_url": "https://hh.ru/vacancy/123"
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    vacancy = result[0]
    assert vacancy["name"] == "Python Developer"
    assert vacancy["id"] == "123"
    assert vacancy["salary"] == {"from": "100000", "to": "150000", "currency": "RUB"}
    assert vacancy["description"] == "Разработка API"
    assert vacancy["url"] == "https://hh.ru/vacancy/123"
    assert vacancy["employer"] == {"id": "1721725", "name": "Rocket10"}



def test_filtered_hh_data_no_salary():
    """Тест: отсутствует поле salary → подставляется дефолтное значение."""
    input_vacancies = [
        {
            "name": "QA Engineer",
            "id": "456",
            "snippet": {"responsibility": "Тестирование"},
            "employer": {"id": "1579449", "name": "idaproject"},
            "alternate_url": "https://hh.ru/vacancy/456"
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    salary = result[0]["salary"]
    assert salary == {"from": "0", "to": "0", "currency": "None"}



def test_filtered_hh_data_salary_not_dict():
    """Тест: salary есть, но не словарь → используется дефолтный salary."""
    input_vacancies = [
        {
            "name": "Designer",
            "id": "789",
            "salary": "not a dict",
            "alternate_url": "https://hh.ru/vacancy/789"
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    salary = result[0]["salary"]
    assert salary == {"from": "0", "to": "0", "currency": "None"}



def test_filtered_hh_data_none_in_salary():
    """Тест: поля from/to в salary равны None → заменяются на '0'."""
    input_vacancies = [
        {
            "name": "Manager",
            "id": "101",
            "salary": {"from": None, "to": None, "currency": "USD"},
            "alternate_url": "https://hh.ru/vacancy/101"
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    salary = result[0]["salary"]
    assert salary == {"from": "0", "to": "0", "currency": "USD"}



def test_filtered_hh_data_no_snippet():
    """Тест: нет snippet/responsibility → description = 'Обязанности не указаны'."""
    input_vacancies = [
        {
            "name": "Analyst",
            "id": "202",
            "salary": {"from": 80000, "to": 120000, "currency": "RUB"},
            "alternate_url": "https://hh.ru/vacancy/202"
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    assert result[0]["description"] == "Обязанности не указаны"



def test_filtered_hh_data_no_employer():
    """Тест: нет employer → employer = None."""
    input_vacancies = [
        {
            "name": "Support",
            "id": "303",
            "salary": {"from": 40000, "to": 60000, "currency": "RUB"},
            "alternate_url": "https://hh.ru/vacancy/303"
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    assert result[0]["employer"] is None



def test_filtered_hh_data_employer_not_dict():
    """Тест: employer есть, но не словарь → employer = None."""
    input_vacancies = [
        {
            "name": "HR",
            "id": "404",
            "employer": "not a dict",
            "alternate_url": "https://hh.ru/vacancy/404"
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    assert result[0]["employer"] is None



def test_filtered_hh_data_no_url():
    """Тест: нет alternate_url → url = 'Нет ссылки'."""
    input_vacancies = [
        {
            "name": "Writer",
            "id": "505",
            "salary": {"from": 30000, "to": 50000, "currency": "RUB"}
        }
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 1
    assert result[0]["url"] == "Нет ссылки"



def test_filtered_hh_data_empty_list():
    """Тест: пустой входной список → пустой результат."""
    result = filtered_hh_data([])
    assert result == []



def test_filtered_hh_data_multiple_vacancies():
    """Тест: несколько вакансий в списке → все обрабатываются."""
    input_vacancies = [
        {"name": "Dev1", "id": "1"},
        {"name": "Dev2", "id": "2", "salary": {"from": 90000, "currency": "RUB"}}
    ]

    result = filtered_hh_data(input_vacancies)

    assert len(result) == 2
    # Первая вакансия: salary дефолтный, url и description по умолчанию
    assert result[0]["salary"] == {"from": "0", "to": "0", "currency": "None"}
    assert result[0]["url"] == "Нет ссылки"
    assert result[0]["description"] == "Обязанности не указаны"
    # Вторая вакансия: salary с from, остальные по умолчанию
    assert result[1]["salary"] == {"from": "90000", "to": "0", "currency": "RUB"}


def test_get_emp_vac_dict_normal_case():
    """Тест: корректные входные данные — оба списка не пустые."""
    employers = [
        {"id": "1721725", "name": "Rocket10"},
        {"id": "1579449", "name": "idaproject"}
    ]
    vacancies = [
        {
            "name": "Python Dev",
            "id": "123",
            "salary": {"from": "100000", "to": "0", "currency": "RUB"},
            "description": "Разработка API",
            "url": "https://example.com",
            "employer": {"id": "1721725", "name": "Rocket10"}
        }
    ]

    result = get_emp_vac_dict(employers, vacancies)

    assert isinstance(result, dict)
    assert "employers" in result
    assert "vacancies" in result
    assert result["employers"] == employers
    assert result["vacancies"] == vacancies



def test_get_emp_vac_dict_empty_employers():
    """Тест: список работодателей пустой — сохраняется как пустой список."""
    employers = []
    vacancies = [
        {
            "name": "QA",
            "id": "456",
            "salary": {"from": "50000", "to": "70000", "currency": "RUB"},
            "description": "Тестирование",
            "url": "https://example.com/qa",
            "employer": None
        }
    ]

    result = get_emp_vac_dict(employers, vacancies)

    assert result["employers"] == []
    assert len(result["vacancies"]) == 1
    assert result["vacancies"][0] == vacancies[0]



def test_get_emp_vac_dict_empty_vacancies():
    """Тест: список вакансий пустой — сохраняется как пустой список."""
    employers = [
        {"id": "1721725", "name": "Rocket10"}
    ]
    vacancies = []

    result = get_emp_vac_dict(employers, vacancies)

    assert len(result["employers"]) == 1
    assert result["employers"][0] == employers[0]
    assert result["vacancies"] == []



def test_get_emp_vac_dict_both_empty():
    """Тест: оба списка пустые — результат содержит пустые списки."""
    result = get_emp_vac_dict([], [])

    assert result["employers"] == []
    assert result["vacancies"] == []



def test_get_emp_vac_dict_single_items():
    """Тест: по одному элементу в каждом списке."""
    employers = [{"id": "1", "name": "Company A"}]
    vacancies = [{"name": "Job 1", "id": "101", "salary": {}, "description": "Desc", "url": "url", "employer": None}]

    result = get_emp_vac_dict(employers, vacancies)

    assert len(result["employers"]) == 1
    assert result["employers"][0] == employers[0]
    assert len(result["vacancies"]) == 1
    assert result["vacancies"][0] == vacancies[0]


def test_get_emp_vac_dict_no_modification():
    """Тест: функция не изменяет входные данные (проверка на мутацию)."""
    employers_orig = [{"id": "1", "name": "Orig"}]
    vacancies_orig = [{"name": "Job", "id": "100"}]

    # Делаем копии, чтобы отследить изменения
    employers_copy = employers_orig.copy()
    vacancies_copy = vacancies_orig.copy()

    result = get_emp_vac_dict(employers_orig, vacancies_orig)

    # Проверяем, что исходные списки не изменились
    assert employers_orig == employers_copy
    assert vacancies_orig == vacancies_copy


    # Проверяем содержимое результата
    assert result["employers"] == employers_orig
    assert result["vacancies"] == vacancies_orig

def test_get_emp_vac_dict_employer_none_in_vacancy():
    """Тест: вакансия с 'employer': None — сохраняется как есть."""
    employers = [{"id": "1", "name": "Comp"}]
    vacancies = [
        {
            "name": "Job",
            "id": "101",
            "salary": {"from": "0", "to": "0", "currency": None},
            "description": "Some duties",
            "url": "https://link",
            "employer": None  # явно None
        }
    ]

    result = get_emp_vac_dict(employers, vacancies)

    assert len(result["vacancies"]) == 1
    assert result["vacancies"][0]["employer"] is None