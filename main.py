
from config import config
from src.hh_data import get_hh_data, filtered_hh_data
from src.db_create import create_database, save_data_to_database


def main():
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

    params = config()

    # ФОРМИРУЕМ ДАННЫЕ ДЛЯ ЗАГРУЗКИ В БД

    # Получаем все вакансии для выбранных работодателей по API
    data = get_hh_data(employers)
    # Оставляем (фильтруем) только нужные данные по вакансиям для загрузки в БД
    filtered_data = filtered_hh_data(data)
    # Формируем словарь данных с работодателями и их вакансиями для загрузки в БД
    emp_vac_dict = get_emp_vac_dict(employers, filtered_data)

    # СОЗДАЕМ БД И ТАБЛИЦЫ employers и vacancies
    # create_database('course3', params)

    # СОХРАНЯЕМ ДАННЫЕ В БД
    # save_data_to_database(data, 'course3', params)


if __name__ == '__main__':
    main()