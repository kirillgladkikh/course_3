class Vacancy:
    """
    Класс для представления вакансии.

    Атрибуты:
        name (str): Название вакансии.
        salary_from (int): Нижняя граница зарплаты.
        salary_to (int): Верхняя граница зарплаты.
        currency (str | None): Валюта зарплаты.
        url (str): Ссылка на вакансию.
        description (str): Описание вакансии.
        **Дополнительные атрибуты**, переданные через **kwargs.

    Примечание:
        Используется __slots__ для оптимизации памяти и ограничения набора атрибутов.
    """

    __slots__ = ("name", "salary_from", "salary_to", "currency", "url", "description", "__dict__")

    def __init__(self, name: str, salary: dict, url: str, description: str, **kwargs) -> None:
        """
        Инициализирует объект Vacancy.

        Args:
            name (str): Название вакансии.
            salary (dict | None): Словарь с полями 'from', 'to', 'currency' или None.
            url (str): Ссылка на вакансию.
            description (str): Описание вакансии.
            **kwargs: Дополнительные атрибуты, которые будут добавлены к объекту.

        Raises:
            TypeError: Если salary не является dict или None.

        Notes:
            - Если salary равен None, зарплата устанавливается как 0–0 без валюты.
            - Дополнительные поля из kwargs добавляются как атрибуты объекта.
        """
        self.name = name
        self.url = url
        self.description = description
        self._validate_salary(salary)

        # Сохраняем дополнительные поля
        for key, value in kwargs.items():
            setattr(self, key, value)

    def _validate_salary(self, salary: dict) -> None:
        """
        Проверяет и обрабатывает данные о зарплате, устанавливая соответствующие атрибуты.

        Args:
            salary (dict | None): Словарь с данными о зарплате или None.

        Sets:
            self.salary_from (int): Нижняя граница зарплаты (0, если не указана).
            self.salary_to (int): Верхняя граница зарплаты (0, если не указана).
            self.currency (str | None): Валюта зарплаты (None, если не указана).

        Raises:
            TypeError: Если salary не является dict или None.
        """
        if salary is None:
            self.salary_from = 0
            self.salary_to = 0
            self.salary_currency = None
        elif isinstance(salary, dict):

            from_value = salary.get("from")
            self.salary_from = 0 if from_value is None else from_value

            to_value = salary.get("to")
            self.salary_to = 0 if to_value is None else to_value

            self.salary_currency = salary.get("currency")

        else:
            raise TypeError(f"salary должен быть dict или None, получено: {type(salary).__name__}")

    def __lt__(self, other) -> bool:
        """
        Определяет поведение оператора «меньше» (<) для сравнения вакансий по нижней границе зарплаты.

        Args:
            other (Vacancy): Другой объект Vacancy для сравнения.

        Returns:
            bool: True, если зарплата текущей вакансии ниже, чем у other; иначе False.

        Raises:
            AttributeError: Если у other нет атрибута salary_from.
        """
        return self.salary_from < other.salary_from

    def __str__(self) -> str:
        """
        Возвращает строковое представление вакансии в читаемом формате.

        Returns:
            str: Многострочное описание вакансии, включающее:
                - название,
                - диапазон зарплаты,
                - валюту,
                - ссылку,
                - описание.
        """
        return (
            f"Название вакансии: {self.name}\n"
            f"Зарплата: от {self.salary_from} до {self.salary_to}\n"
            f"Валюта: {self.salary_currency}\n"
            f"Ссылка: {self.url}\n"
            f"Описание вакансии: {self.description}"
        )


if __name__ == "__main__":
    vac = Vacancy("qwerty", {"from": 1, "to": 10, "currency": "RUR"}, 1, 1)
    print(vac)
