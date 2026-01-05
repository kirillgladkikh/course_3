import requests
import pprint
from abc import ABC, abstractmethod


class AbstractAPI(ABC):
    """
    Абстрактный базовый класс для API‑взаимодействия с сервисами вакансий.

    Определяет контракт для реализации конкретных API‑клиентов (например, для hh.ru).
    Все наследники обязаны реализовать методы подключения и получения вакансий.

    Методы:
        _connect(keyword, per_page):
            Устанавливает соединение/формирует запрос к API с заданными параметрами.
            Должен быть реализован в дочерних классах.

        hh_api_get_vacancies(keyword: str, per_page: int = 20) -> list:
            Получает список вакансий по ключевому слову с указанием количества результатов на страницу.
            Должен быть реализован в дочерних классах.
    """

    @abstractmethod
    def _connect(self, keyword, per_page):
        """
        Абстрактный метод для установления соединения или формирования базового запроса к API.

        Args:
            keyword (str): Ключевое слово для поиска вакансий.
            per_page (int): Количество вакансий, возвращаемых за один запрос (на страницу)

        Raises:
            NotImplementedError: Если метод не переопределён в классе‑наследнике
        """
        pass

    @abstractmethod
    def hh_api_get_vacancies(self, keyword: str, per_page: int = 20) -> list:
        """
        Абстрактный метод для получения списка вакансий из API по ключевому слову.

        Args:
            keyword (str): Ключевое слово для поиска вакансий (например, «Python разработчик»)
            per_page (int, optional): Количество вакансий в ответе (по умолчанию 20)

        Returns:
            list: Список вакансий в формате, определённом реализацией API.
                    Каждый элемент — словарь с данными о вакансии.

        Raises:
            NotImplementedError: Если метод не переопределён в классе‑наследнике
            Exception: Может выбрасывать исключения, связанные с сетью, авторизацией или форматом ответа
                        (конкретика зависит от реализации)
        """
        pass


class HHApi(AbstractAPI):
    """
    Класс для взаимодействия с API сервиса hh.ru (HeadHunter).

    Предоставляет методы для поиска вакансий по ключевому слову и их фильтрации.
    Использует базовый URL API hh.ru и параметры запроса для получения данных.
    """

    def __init__(self):
        """
        Инициализирует экземпляр класса HHApi.

        Устанавливает базовый URL API и пустой словарь параметров запроса.
        """
        self.__url = "https://api.hh.ru/vacancies"
        # self.__params = {"per_page": 20}
        self.__params = {}

    def _connect(self, keyword, per_page):
        """
        Устанавливает соединение с API hh.ru и выполняет запрос.

        Очищает текущие параметры, задаёт новые (ключевое слово и количество
        результатов на страницу), отправляет GET‑запрос и возвращает ответ в формате JSON.

        Args:
            keyword (str): Ключевое слово для поиска вакансий.
            per_page (int): Количество вакансий в ответе (максимум за один запрос)

        Returns:
            dict: JSON‑ответ от API с данными о найденных вакансиях

        Raises:
            requests.HTTPError: Если запрос к API завершился с ошибкой (не 200 OK)
        """
        self.__params.clear()  # + Очищаем старые параметры
        self.__params["text"] = keyword
        self.__params["per_page"] = per_page
        response = requests.get(self.__url, params=self.__params)
        response.raise_for_status()
        return response.json()

    def hh_api_get_vacancies(self, keyword: str, per_page: int = 20) -> list:
        """
        Получает список вакансий по ключевому слову с API hh.ru.

        Выполняет запрос к API через метод _connect, затем фильтрует полученные
        данные с помощью filter_vacancies и возвращает список вакансий.

        Args:
            keyword (str): Ключевое слово для поиска вакансий
            per_page (int, optional): Количество вакансий в ответе. По умолчанию 20

        Returns:
            list: Список словарей с отфильтрованными данными о вакансиях,
                   каждый словарь содержит поля: name, salary, description, url
        """
        response = self._connect(keyword, per_page)
        # print(f'\nresponse["items"]: {response["items"]}')
        return self.filter_vacancies(response["items"])

    @staticmethod
    def filter_vacancies(all_vacancies):
        """
        Фильтрует и структурирует данные о вакансиях из ответа API.

        Извлекает ключевые поля (название, зарплату, описание, URL) из сырых данных API,
        обрабатывает возможные отсутствующие или некорректные значения.

        Args:
            all_vacancies (list): Список словарей — сырые данные о вакансиях из API

        Returns:
            list: Список отфильтрованных словарей с полями:
                - name (str): Название вакансии
                - salary (dict or None): Информация о зарплате (from, to, currency)
                - description (str): Обязанности (из snippet) или сообщение об отсутствии
                - url (str): Ссылка на вакансию или сообщение об отсутствии

        Описание обработки полей:
            - name: берётся напрямую из поля "name" вакансии
            - salary: извлекается из словаря "salary", если он присутствует и корректен
            - description: берётся из "snippet.responsibility", иначе — "Обязанности не указаны"
            - url: берётся из "alternate_url", иначе — "Нет ссылки"
        """
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

            vacancies.append(
                {
                    "name": vacancy["name"],
                    "salary": salary_info,  # vacancy["salary"],
                    "description": responsibility or "Обязанности не указаны",
                    "url": vacancy.get("alternate_url", "Нет ссылки"),  # Проверяем наличие "alternate_url"
                }
            )
        return vacancies


if __name__ == "__main__":
    hh = HHApi()
    vacs = hh.hh_api_get_vacancies("python")

    print("Найденные вакансии:")
    print("=" * 40)

    for i, vac in enumerate(vacs, 1):
        print(f"\n[{i}]")
        pprint.pprint(vac, indent=2, width=60)
    #
    # print(vacs)
    # print([vac["salary"] for vac in hh.filter_vacancies(vacs)])
