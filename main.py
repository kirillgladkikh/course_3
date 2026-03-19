from config import config
from src.hh_data import get_hh_data, filtered_hh_data, get_emp_vac_dict
from src.db_create import create_database, save_data_to_database
from src.db_manager import DBManager


def main():
    """
    Основная функция программы: оркестрация сбора, обработки и сохранения данных о вакансиях и работодателях.

    Последовательность действий:
    1. Определяет список работодателей (по ID на HH).
    2. Получает данные о вакансиях через API HeadHunter.
    3. Фильтрует и структурирует полученные данные.
    4. Формирует единый словарь с данными о работодателях и их вакансиях.
    5. Создаёт базу данных PostgreSQL и необходимые таблицы.
    6. Сохраняет данные в БД.
    7. Создаёт экземпляр DBManager для взаимодействия с БД.
    8. Выводит полный отчёт по данным через метод __str__ класса DBManager.
    9. Закрывает соединение с БД.

    Параметры:
    -----------
    (нет входных параметров — все данные задаются внутри функции)

    Используемые компоненты:
    -----------------------
    - `employers`: список словарей с ID и названиями работодателей на HH.
    - `params`: параметры подключения к PostgreSQL (получаются через функцию `config()`).
    - `get_hh_data()`: получает вакансии для указанных работодателей через API HH.
    - `filtered_hh_data()`: фильтрует и структурирует данные о вакансиях.
    - `get_emp_vac_dict()`: объединяет данные о работодателях и вакансиях в единый словарь.
    - `create_database()`: создаёт БД и таблицы `employers`/`vacancies`.
    - `save_data_to_database()`: сохраняет данные в БД.
    - `DBManager`: класс для взаимодействия с БД (запросы, отчёты).

    Возвращаемое значение:
    ------------------
    None
        Функция не возвращает значение. Результат — сохранённые данные в БД и вывод отчёта в консоль.

    Побочные эффекты:
    -----------------
    - Создаёт БД PostgreSQL с именем 'course3'.
    - Заполняет таблицы `employers` и `vacancies` данными.
    - Печатает полный отчёт по БД в консоль (через `print(db_manager)`).
    - Закрывает соединение с БД.

    Примечания:
    ----------
    - Для работы требуется:
      - Доступ к API HeadHunter (корректные ID работодателей).
      - Настроенный сервер PostgreSQL (доступные параметры в `config()`).
      - Установленные зависимости (psycopg2, requests и др.).
    - В текущем коде часть работодателей закомментирована (например, Яндекс, Тензор).
    - Отчёт выводится через метод `__str__` класса `DBManager`.
    - Соединение с БД закрывается явно (`db_manager.close()`).
    - Ошибки на этапах работы (API, БД) могут привести к прерыванию выполнения.
    """
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

    # ФОРМИРУЕМ ДАННЫЕ ДЛЯ ЗАГРУЗКИ В БД

    # Получаем все вакансии для выбранных работодателей по API
    data = get_hh_data(employers)
    # Оставляем (фильтруем) только нужные данные по вакансиям для загрузки в БД
    filtered_data = filtered_hh_data(data)
    # Формируем словарь данных с работодателями и их вакансиями для загрузки в БД
    emp_vac_dict = get_emp_vac_dict(employers, filtered_data)

    # СОЗДАЕМ БД И ТАБЛИЦЫ employers и vacancies
    create_database("course3", params)

    # СОХРАНЯЕМ ДАННЫЕ В БД
    save_data_to_database(emp_vac_dict, "course3", params)

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
