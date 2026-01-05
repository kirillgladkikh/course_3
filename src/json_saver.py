import json
from abc import ABC, abstractmethod
from pathlib import Path
from src.vacancy import Vacancy


class AbstractFile(ABC):
    """
    Абстрактный базовый класс для работы с файловым хранилищем вакансий.

    Определяет контракт для классов, реализующих взаимодействие с файлами,
    содержащими данные о вакансиях. Включает методы для добавления, сохранения
    и удаления вакансий.

    Методы, помеченные @abstractmethod, обязательны для реализации
    в дочерних классах.

    Методы:
        add_vacancies: Добавляет список вакансий в хранилище.
            Должен быть реализован в дочернем классе.
        save_vacancies_to_json: Сохраняет (записывает) список вакансий в JSON‑файл.
            Реализация по умолчанию предоставляет базовую документацию.
        delete_vacancies: Удаляет вакансии из хранилища.
            Должен быть реализован в дочернем классе.
    """

    # Методы добавления, записи, удаления Вакансий
    @abstractmethod
    def add_vacancies(self, vacancies: list[Vacancy]) -> list[Vacancy]:
        pass

    def save_vacancies_to_json(self, vacancies: list[Vacancy]) -> None:
        pass

    @abstractmethod
    def delete_vacancies(self) -> None:
        pass


class JSONSaver(AbstractFile):
    """
    Класс для работы с JSON‑файлом вакансий.

    Обеспечивает:
    - загрузку существующих вакансий из файла;
    - добавление новых вакансий с проверкой на дубликаты (по URL);
    - сохранение списка вакансий в JSON‑файл;
    - очистку файла (удаление всех вакансий).

    Атрибуты:
        _filename (Path): путь к JSON‑файлу с вакансиями.
    """

    def __init__(self, path: str = "data/vacancies.json") -> None:
        """
        Инициализирует экземпляр JSONSaver.

        Args:
            path (str): путь к JSON‑файлу (по умолчанию "data/vacancies.json").
        """
        self._filename = Path(path)  # Преобразуем в Path!
        # self._filename = path

    def _load_existing_vacancies(self) -> list[Vacancy]:
        """
        Читает существующие вакансии из JSON‑файла.

        Если файл отсутствует или содержит некорректные данные,
        возвращает пустой список.

        Returns:
            list[Vacancy]: список объектов Vacancy (пустой при ошибке/отсутствии файла).

        Raises:
            FileNotFoundError: если файл не найден (обрабатывается внутри метода).
            json.JSONDecodeError: если файл содержит некорректный JSON (обрабатывается).
            KeyError: если в данных отсутствует обязательное поле 'url' (обрабатывается).
            PermissionError: если нет прав на чтение файла (обрабатывается).
        """
        if not self._filename.exists():
            return []

        try:
            with open(self._filename, encoding="utf-8") as f:
                data = json.load(f)

            # Преобразуем словари в объекты Vacancy
            vacancies = []
            for item in data:
                vacancies.append(
                    Vacancy(
                        name=item.get("name", ""),  # Значение по умолчанию
                        salary=item.get("salary", {}),  # Значение по умолчанию
                        # name=item["name"],
                        # salary=item.get("salary", {}),
                        url=item["url"],  # Обязательное поле
                        description=item.get("description", ""),  # Значение по умолчанию
                        # description=item.get("description", "")
                    )
                )
            return vacancies

        except (json.JSONDecodeError, KeyError, FileNotFoundError, PermissionError) as e:
            # Логируем ошибку (опционально)
            print(f"Ошибка при чтении файла {self._filename}: {e}")
        return []

    def add_vacancies(self, vacancies_for_json: list[Vacancy]) -> list[Vacancy]:
        """
        Добавляет новые вакансии в хранилище, исключая дубликаты по URL.

        Считывает существующие вакансии из файла, сравнивает их URL с новыми,
        и возвращает объединённый список (существующие + новые уникальные).

        Фактическая запись в файл не выполняется — для этого нужно вызвать save_vacancies_to_json().

        Args:
            vacancies_for_json (list[Vacancy]): список новых объектов Vacancy для добавления.

        Returns:
            list[Vacancy]: объединённый список вакансий (существующие + новые уникальные).

        Notes:
            Дубликаты определяются по полю `url` объекта Vacancy.
        """
        # Читаем существующие вакансии
        existing_vacancies = self._load_existing_vacancies()

        # Собираем URL существующих вакансий
        existing_urls = {vac.url for vac in existing_vacancies}

        # Отбираем новые вакансии (которых нет в файле)
        new_vacancies = [vac for vac in vacancies_for_json if vac.url not in existing_urls]

        # Объединяем старые и новые вакансии в единый файл (без записи в JSON!)
        all_vacancies = existing_vacancies + new_vacancies
        # self._save_vacancies_to_json(all_vacancies)

        return all_vacancies

    def save_vacancies_to_json(self, vacancies: list[Vacancy]) -> None:
        """
        Сохраняет список объектов Vacancy в JSON‑файл.

        Преобразует объекты Vacancy в словари, включая основные поля
        (name, salary, url, description) и дополнительные атрибуты объекта.

        Args:
            vacancies (list[Vacancy]): список объектов Vacancy для сохранения.

        Side effects:
            Записывает данные в файл по пути `self._filename`.
            Выводит сообщение о успешном сохранении.

        Raises:
            PermissionError: если нет прав на запись в файл.
            TypeError: если объекты в списке не поддерживают преобразование в словарь.
        """
        # Преобразуем объекты Vacancy в словари для JSON
        data = []
        for vac in vacancies:
            data.append(
                {
                    "name": vac.name,
                    "salary": {"from": vac.salary_from, "to": vac.salary_to, "currency": vac.salary_currency},
                    "url": vac.url,
                    "description": vac.description,
                    # Добавляем дополнительные поля, если есть
                    **{
                        k: getattr(vac, k)
                        for k in vac.__dict__
                        if k not in ["name", "salary_from", "salary_to", "salary_currency", "url", "description"]
                    },
                }
            )

        with open(self._filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"\nОбновленный перечень Вакансий успешно сохранен в файл: {self._filename}")

    def delete_vacancies(self) -> None:
        """
        Очищает JSON‑файл, записывая в него пустой список.

        После выполнения метода файл существует, но содержит `[]`.

        Side effects:
            Перезаписывает файл по пути `self._filename` пустым списком.
            Выводит сообщение об успешном удалении.

        Raises:
            PermissionError: если нет прав на запись в файл.
        """
        with open(self._filename, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"\nВакансии успешно удалены из {self._filename}")
