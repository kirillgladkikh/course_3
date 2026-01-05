import requests

# создать запрос к апи для 1 employer id
# передаем в функцию список с employers_ids
# для каждого employer_id
# забираем с сайта все его вакансии
# кладем все вакансии в

def get_hh_data(employers_ids):
    """ """
    pass


def connect(employer_id: str = '1740'):
    """ """
    url = f"https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=100&page=0"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


if __name__ == '__main__':
    response = connect()
    print(f'\nresponse["items"]: {response["items"]}')
