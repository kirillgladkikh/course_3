import requests
from typing import Any

# создать запрос к апи для 1 employer id
# передаем в функцию список с employers_ids
# для каждого employer_id
# забираем с сайта все его вакансии
# кладем все вакансии в

employers_ids = [
    '1721725', # Rocket10
    '1579449',  # idaproject
    # '1740',  # Яндекс
    # '67611',  # Тензор
    # '4614421',  # RedLab
    # '727029',  # PravoTech
    # '2300703',  # Открытая мобильная платформа
    # '819979',  # SkillStaff
    # '1993194',  # YADRO
    # '894410',  # РТЛабс
    # '1473866',  # ООО Сбербанк-Сервис
    # '1057',  # Лаборатория Касперского
]

def get_hh_data(employers_ids: list[str]) -> list[dict[str, Any]]:
    """ """
    hh_data = []
    for emp_id in employers_ids:
        response = connect(emp_id)
        # print(f'\nresponse["items"]: {response["items"]}')
        hh_data.extend(response["items"])
    # print(f'\nhh_data.extend(response["items"]: {hh_data}')
    return hh_data

def connect(employer_id: str = '1740'):
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
                "salary": salary_info,  # vacancy["salary"],
                "description": responsibility or "Обязанности не указаны",
                "url": vacancy.get("alternate_url", "Нет ссылки"),  # Проверяем наличие "alternate_url"
                "employer": employer_info,
            }
        )
    print(f'\nFiltered vacancies: {vacancies}')
    return vacancies


def validate_hh_data(filtered_hh_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """ """
    pass



if __name__ == '__main__':
    data = get_hh_data(employers_ids)
    filtered_data = filtered_hh_data(data)
    # response = connect()
    # print(f'\nresponse["items"]: {response["items"]}')
