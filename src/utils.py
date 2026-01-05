# from collections import defaultdict

from src.vacancy import Vacancy


def print_vacancies(vacancies: list[Vacancy]) -> None:
    """
    Выводит на экран список объектов Vacancy.

    Args:
        vacancies: список объектов Vacancy для вывода
    """
    for vac in vacancies:
        print(vac)


def print_vacancy_obj(obj_for_print: list[Vacancy]) -> None:
    """
    Выводит список объектов Vacancy на экран с нумерацией и разделителями (для отладки).

    Для каждой вакансии:
    - выводит номер в формате [={номер}=]
    - вызывает метод __str__ объекта Vacancy
    - добавляет разделитель из 10 символов "-"

    Args:
        obj_for_print: список объектов Vacancy для вывода

    Returns:
        None
    """
    # Выводим список объектов Vacancy на экран - для отладки
    j = 1
    for vac in obj_for_print:
        print(f"[={j}=]")
        j += 1
        print(vac)  # Использует метод __str__
        print("-" * 10)
    return


def input_with_default(prompt: str, default: str) -> str:
    """
    Запрашивает у пользователя ввод с возможностью использования значения по умолчанию.

    Если пользователь ничего не вводит (пустая строка), возвращается значение default.

    Args:
        prompt: текст приглашения к вводу
        default: значение по умолчанию (используется при пустом вводе)

    Returns:
        Строка — введённое пользователем значение или default
    """
    user_input = input(prompt)
    return user_input if user_input else default


def get_valid_per_page() -> int:
    """
    Запрашивает у пользователя количество вакансий на странице (1–100) с валидацией ввода.

    Повторяет запрос до получения корректного значения:
    - целое число в диапазоне 1–100
    - при ошибке выводит сообщение и запрашивает повторно

    Returns:
        Целое число от 1 до 100 — количество вакансий на странице

    Raises:
        ValueError: если введённое значение не является числом
    """
    while True:
        try:
            per_page = int(input_with_default("Введите количество вакансий на 1 странице API-запроса (1–100): ", "20"))
            if 1 <= per_page <= 100:
                return per_page
            else:
                print("Значение должно быть от 1 до 100.")
        except ValueError:
            print("Пожалуйста, введите целое число.")
    return per_page


def get_valid_top_n() -> int:
    """
    Запрашивает у пользователя количество вакансий для вывода в топ N (1–100).

    Повторяет запрос до получения корректного значения:
    - целое число в диапазоне 1–100
    - при ошибке выводит сообщение и запрашивает повторно

    Returns:
        Целое число от 1 до 100 — количество вакансий для топ-вывода

    Raises:
        ValueError: если введённое значение не является числом
    """
    while True:
        top_n = int(input_with_default("Введите количество вакансий для вывода в топ N (1–100): ", "20"))
        if 1 <= top_n <= 100:
            break
        else:
            print("Значение должно быть от 1 до 100.")
    return top_n


def get_valid_currency(VALID_CURRENCY: list[str]) -> str:
    """
    Запрашивает у пользователя валюту для фильтрации вакансий.

    Повторяет запрос до получения допустимого значения из списка VALID_CURRENCY.
    Ввод приводится к нижнему регистру для сравнения, результат возвращается в верхнем.

    Args:
        VALID_CURRENCY: список допустимых значений валюты (например, ["RUR", "KZT", "UZS"])

    Returns:
        Строка — выбранная валюта в верхнем регистре (например, "RUR")
    """
    while True:
        filter_currency = input_with_default(
            "Введите ключевые слова для фильтрации вакансий - по ВАЛЮТЕ (RUR/KZT/UZS): ", "RUR"
        ).lower()
        if filter_currency in VALID_CURRENCY:
            break
        else:
            print("Валюта должна быть: или RUR или KZT или UZS.")
    return filter_currency.upper()


def vacancy_objects_for_json(filtered_vacancies: list[dict]) -> list[Vacancy]:
    """
    Преобразует список словарей вакансий в список объектов Vacancy.

    Для каждого словаря в filtered_vacancies создаёт объект Vacancy,
    передавая поля name, salary, url, description.

    Args:
        filtered_vacancies: список словарей с данными вакансий

    Returns:
        Список объектов Vacancy с корректно обработанными полями salary_from/salary_to
    """
    vacancies_for_json = []
    for vac_dict in filtered_vacancies:
        vac = Vacancy(
            name=vac_dict["name"], salary=vac_dict["salary"], url=vac_dict["url"], description=vac_dict["description"]
        )
        vacancies_for_json.append(vac)
    return vacancies_for_json
    # Теперь список объектов Vacancy (не словарей!) имеет корректно обработанные поля salary_from/salary_to


def filter_vacancies_by_currency(all_vacancies: list[Vacancy], filter_currency: str) -> list[Vacancy]:
    """
    Фильтрует список вакансий по валюте зарплаты.

    Оставляет только вакансии, где salary_currency совпадает с filter_currency (в верхнем регистре).

    Args:
        all_vacancies: полный список объектов Vacancy
        filter_currency: строка с кодом валюты (например, "RUR")

    Returns:
        Список объектов Vacancy, отфильтрованный по валюте
    """
    filtered = []
    for vacancy in all_vacancies:
        if vacancy.salary_currency == filter_currency.upper():
            filtered.append(vacancy)
    return filtered


def filter_vacancies_by_words(vacancies: list[Vacancy], keywords: list[str]) -> list[Vacancy]:
    """
    Фильтрует вакансии по наличию ключевых слов в описании.

    Поиск выполняется без учёта регистра. Каждое ключевое слово должно встречаться
    хотя бы один раз в описании вакансии (логическое И между словами).

    Args:
        vacancies: список объектов Vacancy для фильтрации
        keywords: список ключевых слов для поиска в описании

    Returns:
        Список объектов Vacancy, в описании которых присутствуют все ключевые слова

    Raises:
        TypeError: если keywords не является списком строк
    """
    # Проверка типов
    if not isinstance(keywords, list):
        raise TypeError("keywords должен быть списком")

    if not all(isinstance(word, str) for word in keywords):
        raise TypeError("все элементы keywords должны быть строками")

    # Если ключевых слов нет, возвращаем исходный список
    if not keywords:
        return vacancies

    filtered = []

    for vacancy in vacancies:
        description = (vacancy.description or "").lower()

        # Проверяем, что все ключевые слова присутствуют в описании
        if all(keyword.lower() in description for keyword in keywords):
            filtered.append(vacancy)

    return filtered


def get_vacancies_by_salary(vacancies: list[Vacancy]) -> list[Vacancy]:
    """
    Отбирает вакансии, у которых указана зарплата (salary_from > 0).

    Args:
        vacancies: список объектов Vacancy

    Returns:
        Список объектов Vacancy, у которых salary_from больше нуля
    """
    result = []
    for vacancy in vacancies:
        if vacancy.salary_from > 0:
            result.append(vacancy)
    return result


def sort_vacancies(vacancies: list[Vacancy]) -> list[Vacancy]:
    """
    Сортирует список вакансий в порядке убывания зарплаты.

    Использует естественный порядок сравнения объектов Vacancy
    (у Vacancy реализован метод __lt__ для сортировки по зарплате).

    Args:
        vacancies: список объектов Vacancy для сортировки

    Returns:
        Отсортированный список объектов Vacancy (по убыванию зарплаты)
    """
    return sorted(vacancies, reverse=True)


def get_top_vacancies(sorted_vacancies: list[Vacancy], top_n: int) -> list[Vacancy]:
    """
    Возвращает топ-N вакансий из отсортированного списка.

    Args:
        sorted_vacancies: список объектов Vacancy, предварительно отсортированный
                    (по убыванию зарплаты)
        top_n: количество вакансий для включения в топ (целое положительное число)

    Returns:
        Список из top_n объектов Vacancy (или меньше, если исходный список короче)

    Raises:
        ValueError: если top_n отрицательное
        TypeError: если top_n не является целым числом
    """
    # Проверка типов и значений
    if not isinstance(top_n, int):
        raise TypeError("top_n должен быть целым числом")

    if top_n < 0:
        raise ValueError("top_n не может быть отрицательным")

    # Возвращаем срез списка: первые top_n элементов
    # Если список короче top_n, вернём всё, что есть
    return sorted_vacancies[:top_n]


def print_vacancy_count(sorted_vacancies: list[Vacancy], top_n: int) -> None:
    """
    Выводит информацию о количестве найденных вакансий и числе отображаемых на экране.

    Функция принимает отсортированный список вакансий и количество вакансий для отображения,
    сравнивает их с общим количеством доступных вакансий и выводит информативное сообщение.

    Args:
        sorted_vacancies (list[Vacancy]): Отсортированный список объектов Vacancy,
            соответствующих поисковым условиям.
        top_n (int): Количество вакансий, которые планируется вывести на экран.
            Если значение превышает общее количество доступных вакансий, будет использовано
            максимально возможное число.

    Returns:
        None: Функция выполняет вывод в консоль и не возвращает значение.
    """
    # Получаем количество доступных вакансий
    total_available = len(sorted_vacancies)

    if top_n > total_available:
        top_n = total_available

    # Выводим информационное сообщение
    print(f"Всего нашлось {total_available} вакансий под заданные условия.\nНа экран выведено {top_n} вакансий.")

    return
