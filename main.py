from src.hh_api import HHApi

# from src.vacancy import Vacancy
from src.json_saver import JSONSaver
from src.utils import (
    print_vacancy_obj,
    input_with_default,
    get_valid_per_page,
    get_valid_top_n,
    get_valid_currency,
    vacancy_objects_for_json,
    filter_vacancies_by_currency,
    filter_vacancies_by_words,
    get_vacancies_by_salary,
    sort_vacancies,
    get_top_vacancies,
    print_vacancy_count,
)


# Возможен поиск по следующим валютам:
VALID_CURRENCY = ["rur", "kzt", "uzs"]


# Функция для взаимодействия с пользователем
def user_interaction() -> None:
    """
    Интерактивная функция для взаимодействия с пользователем при поиске и обработке вакансий.

    Последовательность действий:
    1. Запрашивает у пользователя параметры поиска и фильтрации вакансий:
       - необходимость очистки существующего JSON‑файла;
       - поисковый запрос;
       - количество вакансий на странице API‑запроса (1–100);
       - количество вакансий для вывода в топ‑N (1–100);
       - валюту для фильтрации зарплат (из списка VALID_CURRENCY).

    2. Обрабатывает запросы:
       - при необходимости очищает JSON‑файл с вакансиями;
       - выполняет API‑запрос к HH.ru с указанными параметрами;
       - преобразует полученные данные в объекты Vacancy;
       - добавляет новые вакансии в существующий JSON‑файл.

    3. Фильтрует и сортирует вакансии:
       - оставляет только вакансии с выбранной валютой;
       - убирает вакансии с нулевыми значениями зарплаты;
       - сортирует вакансии по убыванию зарплаты;
       - формирует топ‑N вакансий по запросу пользователя.

    4. Выводит результаты:
       - топ‑N вакансий в консоль;
       - общее количество подходящих вакансий.

    Используемые внешние компоненты:
    - HHApi: для взаимодействия с API hh.ru;
    - JSONSaver: для сохранения/чтения вакансий в JSON‑файл;
    - Vacancy: класс для представления вакансии;
    - вспомогательные функции из src.utils: для валидации ввода, фильтрации, сортировки и вывода данных.

    Глобальные константы:
    - VALID_CURRENCY: список допустимых валют для фильтрации ('rur', 'kzt', 'uzs').

    Возвращаемое значение:
    - None (функция выполняет действия, но не возвращает результат).
    """
    # ВВОД ПОЛЬЗОВАТЕЛЕМ ИСХОДНЫХ ДАННЫХ

    # Запрашивает у пользователя необходимость очистки существующего JSON-файла Вакансий.
    # по-умолчанию clear_json = "0"
    clear_json = input_with_default("Очистить текущий JSON с Вакансиями? (0 - НЕТ, любой символ - ДА): ", "0")
    print(f"clear_json = {clear_json}")

    # Запрашивает у пользователя поисковый запрос.
    # по-умолчанию search_query = "python"
    search_query = input_with_default("Введите поисковый запрос: ", "python").lower()
    print(f"search_query = {search_query}")

    # Запрашивает у пользователя количество вакансий на 1 странице API-запроса (1–100) с валидацией.
    # по-умолчанию per_page = 20
    per_page = get_valid_per_page()
    print(f"per_page = {per_page}")

    # Запрашивает у пользователя количество вакансий для вывода в топ N (1–100) с валидацией.
    # по-умолчанию per_page = 20
    top_n = get_valid_top_n()
    print(f"top_n = {top_n}")

    # Запрашивает у пользователя ключевые слова для фильтрации вакансий - по описанию.
    # по-умолчанию filter_words = "backend"
    filter_words = input_with_default(
        "Введите ключевые слова для фильтрации вакансий - по описанию: ", "backend"
    ).split()
    # filter_words = input("Введите ключевые слова для фильтрации вакансий - по описанию: ").split()
    print(f"filter_words = {filter_words}")

    # Запрашивает у пользователя ключевые слова для фильтрации вакансий - по ВАЛЮТЕ (RUR/KZT/UZS) с валидацией.
    # по-умолчанию filter_currency = "RUR"
    filter_currency = get_valid_currency(VALID_CURRENCY)
    print(f"filter_currency = {filter_currency}")

    # ОБРАБОТКА ЗАПРОСОВ ПОЛЬЗОВАТЕЛЯ

    # ОЧИСТКА JSON - если таков выбор пользователя
    # - cоздаём экземпляр saver (файл сохранится в data/vacancies.json)
    saver = JSONSaver("data/vacancies.json")
    # - очищаем JSON если таков выбор пользователя
    if clear_json != "0":
        saver.delete_vacancies()

    # Создание экземпляра класса для работы с API сайтов с вакансиями
    hh = HHApi()
    # Получение filtered_vacancies: !!!список словарей!!!
    # УЖЕ ОТФИЛЬТРОВАННЫХ ПОЛЕЙ (name, salary, url, description) вакансий с hh.ru
    hh_api_filtered_vacancies = hh.hh_api_get_vacancies(search_query, per_page)

    # Формируем vacancies_for_json: список объектов Vacancy (не словарей!)
    # с корректно обработанными полями salary_from/salary_to/currency
    vacancies_for_json = vacancy_objects_for_json(hh_api_filtered_vacancies)
    # print_vacancy_obj(vacancies_for_json)

    # По введенным пользователей условиям: search_query, per_page
    # - открываем существующий JSON
    # - добавляем новые вакансии из vacancies_for_json
    # - сохраняем "старое"+"новое" в all_vacancies
    all_vacancies = saver.add_vacancies(vacancies_for_json)
    # print_vacancy_obj(all_vacancies)

    saver.save_vacancies_to_json(
        all_vacancies
    )  # Записываем all_vacancies в JSON-файл (предварительно преобразуя объекты Vacancy в словари!)

    # ФИЛЬТРУЕМ, СОРТИРУЕМ, ВЫВОДИМ ТОП ВАКАНСИЙ

    # Оставляем только выбранную пользователем валюту зарплаты
    filtered_vacancies_by_currency = filter_vacancies_by_currency(all_vacancies, filter_currency)
    # print_vacancy_obj(filtered_vacancies_by_currency)

    # Оставляем только вакансии содержащие выбранные пользователем ключевые слова в описании.
    filtered_vacancies_by_words = filter_vacancies_by_words(filtered_vacancies_by_currency, filter_words)
    # print_vacancy_obj(filtered_vacancies_by_words)

    # Убираем из списка вакансии с нулями в зарплате
    ranged_vacancies = get_vacancies_by_salary(filtered_vacancies_by_words)
    # print_vacancy_obj(ranged_vacancies)

    # Сортируем вакансии по убыванию
    sorted_vacancies = sort_vacancies(ranged_vacancies)
    # print_vacancy_obj(sorted_vacancies)

    # Формируем TOP-N список вакансий
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n)

    # Выводим в консоль TOP-N вакансий сформированный под условия пользователя
    print_vacancy_obj(top_vacancies)

    # Выводим в консоль сообщение о количестве ВСЕХ полученных вакансий под условия пользователя
    print_vacancy_count(sorted_vacancies, top_n)

    return


if __name__ == "__main__":
    user_interaction()
