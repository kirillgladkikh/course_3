import requests
from typing import Any

# создать запрос к апи для 1 employer id
# передаем в функцию список с employers_ids
# для каждого employer_id
# забираем с сайта все его вакансии
# кладем все вакансии в

# employers_ids = [
#     '1721725', # Rocket10
#     '1579449',  # idaproject
#     '1740',  # Яндекс
#     '67611',  # Тензор
#     '4614421',  # RedLab
#     '727029',  # PravoTech
#     '2300703',  # Открытая мобильная платформа
#     '819979',  # SkillStaff
#     '1993194',  # YADRO
#     '894410',  # РТЛабс
#     '1473866',  # ООО Сбербанк-Сервис
#     '1057',  # Лаборатория Касперского
# ]

employers = [
    {"employer_id": "1721725", "name": "Rocket10"},
    {"employer_id": "1579449", "name": "idaproject"},
    # {"employer_id": "1740", "name": "Яндекс"},
    # {"employer_id": "67611", "name": "Тензор"},
    # {"employer_id": "4614421", "name": "RedLab"},
    # {"employer_id": "727029", "name": "PravoTech"},
    # {"employer_id": "2300703", "name": "Открытая мобильная платформа"},
    # {"employer_id": "819979", "name": "SkillStaff"},
    # {"employer_id": "1993194", "name": "YADRO"},
    # {"employer_id": "894410", "name": "РТЛабс"},
    # {"employer_id": "1473866", "name": "ООО Сбербанк-Сервис"},
    # {"employer_id": "1057", "name": "Лаборатория Касперского"}
]


def get_hh_data(employers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """ """
    hh_data = []
    for employer in employers:
        emp_id = employer["employer_id"]  # берём ID из словаря

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
    """ """
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=100&page=0"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def filtered_hh_data(all_vacancies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """ """
    vacancies = []
    for vacancy in all_vacancies:

        # 1. Проверяем наличие 'snippet' и 'responsibility'
        responsibility = None
        if (
                vacancy.get("snippet")
                and isinstance(vacancy["snippet"], dict)
                and "responsibility" in vacancy["snippet"]
        ):
            responsibility = vacancy["snippet"]["responsibility"]

        # 2. Проверка поля 'salary'
        salary_info = None

        # Сценарий 1: salary присутствует в вакансии
        if "salary" in vacancy:
            salary = vacancy["salary"]

            # Сценарий 2: salary — словарь (корректный формат)
            if isinstance(salary, dict):
                salary_info = {
                    "from": salary.get("from"),
                    "to": salary.get("to"),
                    "currency": salary.get("currency"),
                }
            # Сценарий 3: salary ОТСУТСТВУЕТ в вакансии
            else:
                salary_info = {
                    "from": "0",
                    "to": "0",
                    "currency": None
                }

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


def get_emp_vac_dict(employers: list[dict[str, Any]], filtered_hh_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """ """
    result = {
        "employers": employers,
        "vacancies": filtered_hh_data
    }
    print(f'\nemp_vac_dict: {[result]}')
    return [result]  # Обернули словарь в список
    # emp_vac_dict = []
    # emp_vac_dict['employers'] = employers
    # emp_vac_dict.append['vacancies'] = filtered_hh_data
    #
    # return emp_vac_dict


if __name__ == '__main__':
    data = get_hh_data(employers)
    filtered_data = filtered_hh_data(data)
    get_emp_vac_dict(employers, filtered_data)
    # response = connect()
    # print(f'\nresponse["items"]: {response["items"]}')
