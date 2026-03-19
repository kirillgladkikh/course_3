import requests
from typing import Any


# employers = [
#     {"id": "1721725", "name": "Rocket10"},
#     {"id": "1579449", "name": "idaproject"},
#     # {"id": "1740", "name": "Яндекс"},
#     # {"id": "67611", "name": "Тензор"},
#     # {"id": "4614421", "name": "RedLab"},
#     # {"id": "727029", "name": "PravoTech"},
#     # {"id": "2300703", "name": "Открытая мобильная платформа"},
#     # {"id": "819979", "name": "SkillStaff"},
#     # {"id": "1993194", "name": "YADRO"},
#     # {"id": "894410", "name": "РТЛабс"},
#     # {"id": "1473866", "name": "ООО Сбербанк-Сервис"},
#     # {"id": "1057", "name": "Лаборатория Касперского"}
# ]


def get_hh_data(employers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Получает данные о вакансиях с HeadHunter API для списка работодателей.

    Функция последовательно запрашивает API HH для каждого работодателя из входного списка,
    извлекает список вакансий (поле 'items') и объединяет их в единый результат.

    Параметры:
    -----------
    employers : list[dict[str, Any]]
        Список словарей с данными о работодателях. Каждый словарь должен содержать ключ 'id'
        с идентификатором работодателя на HH. Пример:
        [
            {"id": "1721725", "name": "Rocket10"},
            {"id": "1579449", "name": "idaproject"}
        ]

    Возвращаемое значение:
    ------------------
    list[dict[str, Any]]
        Список словарей, представляющих вакансии. Каждый словарь — это данные о вакансии
        в формате, возвращаемом API HH (содержит поля вроде 'id', 'name', 'salary' и др.).
        Если для какого-то работодателя данные не удалось получить, он пропускается
        с выводом предупреждения/сообщения об ошибке.

    Побочные эффекты:
    -----------------
    - Печатает предупреждения, если в ответе API отсутствует список вакансий ('items').
    - Печатает сообщения об ошибках при неудачных запросах к API.

    Примечания:
    ----------
    - Функция зависит от вспомогательной функции `connect(emp_id)`, которая должна
      выполнять HTTP-запрос к API HH и возвращать JSON-ответ.
    - Обработка ошибок реализована через try-except; неудачные запросы не прерывают
      выполнение функции, а лишь логируются.
    """
    hh_data = []
    for employer in employers:
        emp_id = employer["id"]  # берём ID из словаря

        try:
            response = connect(emp_id)  # предполагаем, что connect() возвращает JSON-ответ API
            # print(f'\nresponse["items"]: {response["items"]}')

            # Проверяем наличие ключа "items" и что это список
            if "items" in response and isinstance(response["items"], list):
                hh_data.extend(response["items"])
                # print(f'\nhh_data.extend(response["items"]: {hh_data}')
            else:
                print(f"Предупреждение: в ответе для employer_id={emp_id} нет списка 'items'")

        except Exception as e:
            print(f"Ошибка при получении данных для employer_id={emp_id} ({employer['name']}): {e}")

    return hh_data


def connect(employer_id: str):
    """
    Выполняет HTTP‑запрос к API HeadHunter для получения вакансий указанного работодателя.

    Параметры:
    -----------
    employer_id : str
        Идентификатор работодателя на платформе HeadHunter (HH). Должен быть допустимой
        строкой, соответствующей формату ID на HH (например, "1721725").

    Возвращаемое значение:
    ------------------
    dict
        JSON‑ответ API HH в виде словаря. Содержит поле 'items' со списком вакансий,
        а также служебные поля (например, 'found', 'page', 'pages' и др.).
        Структура соответствует документации API HH.

    Исключения:
    -----------
    requests.exceptions.HTTPError
        Если сервер вернул код ошибки (4xx, 5xx), метод `raise_for_status()`
        пробросит соответствующее исключение.
    requests.exceptions.RequestException
        Если возникла проблема с сетевым запросом (нет соединения, тайм‑аут и т. п.).
    ValueError
        Если ответ сервера не может быть декодирован как JSON.

    Побочные эффекты:
    -----------------
    - Выполняет сетевой HTTP‑запрос к `https://api.hh.ru/vacancies`.
    - Повышает исключение при коде ответа, отличном от 2xx.

    Примечания:
    ----------
    - URL включает параметры:
      - `employer_id` — фильтр по работодателю;
      - `per_page=100` — максимальное число вакансий на страницу (лимит API);
      - `page=0` — первая страница результатов.
    - Для обработки пагинации (если вакансий больше 100) потребуется дополнительный код.
    - Требуется наличие установленной библиотеки `requests`.
    """
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=100&page=0"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def filtered_hh_data(all_vacancies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Фильтрует и структурирует данные о вакансиях из ответа API HeadHunter.

    Для каждой вакансии из входного списка:
    - извлекает обязанности из поля 'snippet.responsibility';
    - обрабатывает информацию о зарплате, приводя её к унифицированному формату;
    - получает данные о работодателе;
    - формирует итоговый словарь с фиксированным набором полей.

    Параметры:
    -----------
    all_vacancies : list[dict[str, Any]]
        Список словарей, представляющих вакансии в формате ответа API HH.
        Каждый словарь должен содержать (как минимум) поля:
        - 'name' (название вакансии)
        - 'id' (идентификатор вакансии)
        - опционально: 'snippet', 'salary', 'employer', 'alternate_url'

    Возвращаемое значение:
    ------------------
    list[dict[str, Any]]
        Список отфильтрованных и структурированных вакансий. Каждая вакансия — словарь со полями:
        - 'name' (str): название вакансии
        - 'id' (str): идентификатор вакансии
        - 'salary' (dict): информация о зарплате с ключами:
          - 'from' (str): нижняя граница зарплаты ('0' если отсутствует/None)
          - 'to' (str): верхняя граница зарплаты ('0' если отсутствует/None)
          - 'currency' (str or None): валюта зарплаты
        - 'description' (str): обязанности (из 'snippet.responsibility') или
          сообщение 'Обязанности не указаны'
        - 'url' (str): ссылка на вакансию ('Нет ссылки' если отсутствует)
        - 'employer' (dict or None): данные о работодателе с ключами:
          - 'id' (str or None)
          - 'name' (str or None)

    Побочные эффекты:
    -----------------
    - Не производит вывод в консоль (закомментированный print удалён).
    - Не изменяет входные данные.

    Примечания:
    ----------
    - Для поля 'salary' значения 'from' и 'to' всегда возвращаются как строки.
      Если исходное значение None — подставляется '0'.
    - Если поле 'salary' отсутствует или не является словарём, возвращается
      дефолтный словарь с 'from'='0', 'to'='0', 'currency'='None'.
    - Поле 'currency' может быть None, если отсутствует в исходных данных.
    - Для 'description' используется 'responsibility' из 'snippet', иначе —
      запасной текст.
    - Ссылка 'url' берётся из 'alternate_url', иначе — 'Нет ссылки'.
    - Данные о работодателе включаются только если 'employer' присутствует и является
      словарём.
    """
    vacancies = []
    for vacancy in all_vacancies:

        # 1. Проверяем наличие 'snippet' и 'responsibility'
        responsibility = None
        if vacancy.get("snippet") and isinstance(vacancy["snippet"], dict) and "responsibility" in vacancy["snippet"]:
            responsibility = vacancy["snippet"]["responsibility"]

        # 2. Проверка поля 'salary'
        salary_info = None

        # Сценарий 1: salary присутствует в вакансии
        if "salary" in vacancy:
            salary = vacancy["salary"]

            # Сценарий 2: salary — словарь (корректный формат)
            if isinstance(salary, dict):

                # Явная проверка на None для from/to
                salary_from = salary.get("from")
                salary_to = salary.get("to")

                salary_info = {
                    "from": str(salary_from) if salary_from is not None else "0",
                    "to": str(salary_to) if salary_to is not None else "0",
                    "currency": salary.get("currency"),
                }
            else:
                salary_info = {"from": "0", "to": "0", "currency": "None"}

            # Сценарий 3: salary ОТСУТСТВУЕТ в вакансии
        else:
            salary_info = {"from": "0", "to": "0", "currency": "None"}

        # 3. Проверка поля "employer"
        employer_info = None

        # Сценарий 1: employer присутствует в вакансии
        if "employer" in vacancy:
            employer = vacancy["employer"]

            # Сценарий 2: employer — словарь (корректный формат)
            if isinstance(employer, dict):
                employer_info = {
                    "id": employer.get("id"),
                    "name": employer.get("name"),
                }

        vacancies.append(
            {
                "name": vacancy["name"],
                "id": vacancy["id"],
                "salary": salary_info,
                "description": responsibility or "Обязанности не указаны",
                "url": vacancy.get("alternate_url", "Нет ссылки"),  # Проверяем наличие "alternate_url"
                "employer": employer_info,
            }
        )
    # print(f'\nFiltered vacancies: {vacancies}')
    return vacancies


def get_emp_vac_dict(employers: list[dict[str, Any]], filtered_hh_data: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Формирует словарь, объединяющий данные о работодателях и отфильтрованных вакансиях.

    Функция принимает два списка — работодателей и обработанных вакансий — и упаковывает
    их в единый словарь с фиксированными ключами. Это удобно для дальнейшей передачи
    данных в другие компоненты системы (например, для сохранения в БД).

    Параметры:
    -----------
    employers : list[dict[str, Any]]
        Список словарей с данными о работодателях. Каждый словарь должен содержать
        как минимум поля:
        - 'id' (идентификатор работодателя)
        - 'name' (название работодателя)
        Пример:
        [
            {"id": "1721725", "name": "Rocket10"},
            {"id": "1579449", "name": "idaproject"}
        ]

    filtered_hh_data : list[dict[str, Any]]
        Список отфильтрованных и структурированных вакансий (результат работы
        функции `filtered_hh_data`). Каждая вакансия — словарь со полями:
        - 'name' (название вакансии)
        - 'id' (идентификатор вакансии)
        - 'salary' (информация о зарплате)
        - 'description' (описание обязанностей)
        - 'url' (ссылка на вакансию)
        - 'employer' (данные о работодателе, может быть None)

    Возвращаемое значение:
    ------------------
    dict[str, Any]
        Словарь с двумя ключами:
        - 'employers': список переданных работодателей
        - 'vacancies': список переданных отфильтрованных вакансий
        Пример:
        {
            "employers": [
                {"id": "1721725", "name": "Rocket10"},
                ...
            ],
            "vacancies": [
                {
                    "name": "Python Developer",
                    "id": "123",
                    "salary": {"from": "100000", "to": "0", "currency": "RUB"},
                    "description": "Разработка API",
                    "url": "https://...",
                    "employer": {"id": "1721725", "name": "Rocket10"}
                },
                ...
            ]
        }

    Побочные эффекты:
    -----------------
    - Не изменяет входные данные.
    - Не производит вывод в консоль (закомментированный print удалён).

    Примечания:
    ----------
    - Функция выполняет простую упаковку данных без дополнительной обработки.
    - Ожидаются корректно сформированные входные списки (проверка типов не выполняется).
    - Результат подходит для передачи в функцию сохранения данных в БД
      (например, `save_data_to_database`).
    """
    result = {"employers": employers, "vacancies": filtered_hh_data}
    # print(f"\nemp_vac_dict: {result}")
    return result


if __name__ == "__main__":
    data = get_hh_data(employers)
    filtered_data = filtered_hh_data(data)
    get_emp_vac_dict(employers, filtered_data)
