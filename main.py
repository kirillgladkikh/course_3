from config import config
from src.hh_data import get_hh_data, filtered_hh_data, get_emp_vac_dict
from src.db_create import create_database, save_data_to_database
from src.db_manager import DBManager


def main():
    # Список словарей данных о 10 работодателях:
    employers = [
        {"id": "1721725", "name": "Rocket10"},
        {"id": "1579449", "name": "idaproject"},
        # {"id": "1740", "name": "Яндекс"},
        # {"id": "67611", "name": "Тензор"},
        {"id": "4614421", "name": "RedLab"},
        {"id": "727029", "name": "PravoTech"},
        {"id": "2300703", "name": "Открытая мобильная платформа"},
        {"id": "819979", "name": "SkillStaff"},
        {"id": "1993194", "name": "YADRO"},
        {"id": "894410", "name": "РТЛабс"},
        {"id": "1473866", "name": "ООО Сбербанк-Сервис"},
        {"id": "1057", "name": "Лаборатория Касперского"},
    ]

    params = config()

    # # ФОРМИРУЕМ ДАННЫЕ ДЛЯ ЗАГРУЗКИ В БД
    #
    # # Получаем все вакансии для выбранных работодателей по API
    # data = get_hh_data(employers)
    # # Оставляем (фильтруем) только нужные данные по вакансиям для загрузки в БД
    # filtered_data = filtered_hh_data(data)
    # # Формируем словарь данных с работодателями и их вакансиями для загрузки в БД
    # emp_vac_dict = get_emp_vac_dict(employers, filtered_data)
    #
    # # СОЗДАЕМ БД И ТАБЛИЦЫ employers и vacancies
    # create_database('course3', params)
    #
    # # СОХРАНЯЕМ ДАННЫЕ В БД
    # save_data_to_database(emp_vac_dict, 'course3', params)

    # ВЗАИМОДЕЙСТВИЕ С БД

    # Создаём менеджер БД
    db_manager = DBManager("course3", params)

    # Вызовы методов указанных в ДЗ выполняются внутри класса DBManager:
    # companies = self.get_companies_and_vacancies_count()
    # all_vacancies = self.get_all_vacancies()
    # avg_salary = self.get_avg_salary()
    # high_salary_vacancies = self.get_vacancies_with_higher_salary()
    # # Для примера возьмём ключевое слово 'python'
    # keyword_vacancies = self.get_vacancies_with_keyword("python")

    # Вызов __str__ и вывод всего отчёта
    print(db_manager)

    # Закрыть соединение
    db_manager.close()


if __name__ == "__main__":
    main()
