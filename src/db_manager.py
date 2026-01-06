import psycopg2
from typing import List, Dict, Optional, Any


class DBManager:
    def __init__(self, db_name: str, db_params: dict[str, Any]):
        """
        Инициализация менеджера БД.

        :param db_name: название базы данных
        :param db_params: параметры подключения (user, password, host, etc.)
        """
        self.db_name = db_name
        self.db_params = db_params
        self.conn = None

    def connect(self):
        """Устанавливает соединение с БД."""
        try:
            self.conn = psycopg2.connect(dbname=self.db_name, **self.db_params)
        except Exception as e:
            raise ConnectionError(f"Ошибка подключения к БД: {e}")

    def close(self):
        """Закрывает соединение с БД."""
        if self.conn:
            self.conn.close()

    def get_companies_and_vacancies_count(self) -> list[dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой.

        :return: список словарей с ключами 'company_name' и 'vacancies_count'
        """
        if not self.conn:
            self.connect()

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name AS company_name, COUNT(v.vacancy_id) AS vacancies_count
                FROM employers e
                LEFT JOIN vacancies v ON e.employer_id = v.employer_id
                GROUP BY e.employer_id, e.name
                ORDER BY vacancies_count DESC;
            """)
            rows = cur.fetchall()

        return [
            {"company_name": row[0], "vacancies_count": row[1]}
            for row in rows
        ]

    def get_all_vacancies(self) -> list[dict[str, Any]]:
        """
        Получает все вакансии с информацией о компании, названии, зарплате и ссылке.

        :return: список словарей с полями:
                 'company_name', 'vacancy_name', 'salary_from', 'salary_to', 'currency', 'url'
        """
        if not self.conn:
            self.connect()

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id;
            """)
            rows = cur.fetchall()

        return [
            {
                "company_name": row[0],
                "vacancy_name": row[1],
                "salary_from": row[2],
                "salary_to": row[3],
                "currency": row[4],
                "url": row[5]
            }
            for row in rows
        ]

    def get_avg_salary(self) -> float:
        """
        Вычисляет среднюю зарплату по всем вакансиям (среднее между salary_from и salary_to).

        :return: средняя зарплата (float)
        """
        if not self.conn:
            self.connect()

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT AVG((NULLIF(salary_from, '0')::numeric + NULLIF(salary_to, '0')::numeric) / 2)
                FROM vacancies;
            """)
            result = cur.fetchone()[0]

        return float(result) if result is not None else 0.0

    def get_vacancies_with_higher_salary(self) -> list[dict[str, Any]]:
        """
        Получает вакансии, где средняя зарплата выше общей средней.

        :return: список вакансий (аналогично get_all_vacancies)
        """
        avg_salary = self.get_avg_salary()
        if not self.conn:
            self.connect()

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE ((NULLIF(v.salary_from, '0')::numeric + NULLIF(v.salary_to, '0')::numeric) / 2) > %s;
            """, (avg_salary,))
            rows = cur.fetchall()

        return [
            {
                "company_name": row[0],
                "vacancy_name": row[1],
                "salary_from": row[2],
                "salary_to": row[3],
                "currency": row[4],
                "url": row[5]
            }
            for row in rows
        ]

    def get_vacancies_with_keyword(self, keyword: str) -> list[dict[str, Any]]:
        """
        Получает вакансии, в названии которых есть указанное ключевое слово.

        :param keyword: ключевое слово для поиска
        :return: список вакансий (аналогично get_all_vacancies)
        """
        if not self.conn:
            self.connect()

        # Используем ILIKE для регистронезависимого поиска
        search_pattern = f"%{keyword}%"

        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
                FROM vacancies v
                JOIN employers e ON v.employer_id = e.employer_id
                WHERE v.name ILIKE %s;
            """, (search_pattern,))
            rows = cur.fetchall()

        return [
            {
                "company_name": row[0],
                "vacancy_name": row[1],
                "salary_from": row[2],
                "salary_to": row[3],
                "currency": row[4],
                "url": row[5]
            }
            for row in rows
        ]


    def _format_companies(self, data: list[dict[str, Any]]) -> str:
        if not data:
            return "▸ Компании: не найдены."
        lines = ["▸ Компании и количество вакансий:"]
        for item in data:
            lines.append(f"  • {item['company_name']} — {item['vacancies_count']} вакансий")
        return "\n".join(lines)

    def _format_vacancies(self, data: list[dict[str, Any]]) -> str:
        if not data:
            return "▸ Вакансии: не найдены."
        lines = ["▸ Все вакансии:"]
        for item in data:
            lines.append(
                f"  • Компания: {item['company_name']}\n"
                f"    Название: {item['vacancy_name']}\n"
                f"    Зарплата: {item['salary_from']} – {item['salary_to']} {item['currency']}\n"
                f"    Ссылка: {item['url']}"
            )
        return "\n".join(lines)

    def _format_avg_salary(self, value: float) -> str:
        return f"▸ Средняя зарплата по вакансиям: {value:.2f} RUB"
        # return f"▸ Средняя зарплата по вакансиям: {value:.2f} {self._detect_common_currency() or 'RUB'}"


    def _format_high_salary_vacancies(self, data: list[dict[str, Any]]) -> str:
        if not data:
            return "▸ Вакансии с зарплатой выше средней: не найдены."
        lines = ["▸ Вакансии с зарплатой выше средней:"]
        for item in data:
            avg = (float(item['salary_from']) + float(item['salary_to'])) / 2
            lines.append(
                f"  • Компания: {item['company_name']}\n"
                f"    Название: {item['vacancy_name']}\n"
                f"    Средняя зарплата: {avg:.2f} {item['currency']}\n"
                f"    Ссылка: {item['url']}"
            )
        return "\n".join(lines)


    def _format_keyword_vacancies(self, keyword: str, data: list[dict[str, Any]]) -> str:
        if not data:
            return f"▸ Вакансии по ключевому слову '{keyword}': не найдены."
        lines = [f"▸ Вакансии по ключевому слову '{keyword}':"]
        for item in data:
            lines.append(
                f"  • Компания: {item['company_name']}\n"
                f"    Название: {item['vacancy_name']}\n"
                f"    Зарплата: {item['salary_from']} – {item['salary_to']} {item['currency']}\n"
                f"    Ссылка: {item['url']}"
            )
        return "\n".join(lines)

    def _detect_common_currency(self) -> Optional[str]:
        """Определяет наиболее частую валюту в вакансиях (для подписи средней зарплаты)."""
        if not self.conn:
            self.connect()
        with self.conn.cursor() as cur:
            cur.execute("SELECT currency, COUNT(*) as cnt FROM vacancies GROUP BY currency ORDER BY cnt DESC LIMIT 1")
            result = cur.fetchone()
        return result[0] if result else None


    def __str__(self) -> str:
        """
        Возвращает полный отформатированный отчёт по данным БД.
        Вызывает все методы и собирает результаты в единый читаемый текст.
        """
        try:
            if not self.conn:
                self.connect()

            # Собираем все данные
            companies = self.get_companies_and_vacancies_count()
            all_vacancies = self.get_all_vacancies()
            avg_salary = self.get_avg_salary()
            high_salary_vacancies = self.get_vacancies_with_higher_salary()
            # Для примера возьмём ключевое слово 'python'
            keyword_vacancies = self.get_vacancies_with_keyword("python")


            # Формируем отчёт
            report = (
                "= ОТЧЁТ ПО БАЗЕ ДАННЫХ =\n\n"
                + self._format_companies(companies) + "\n\n"
                + self._format_vacancies(all_vacancies) + "\n\n"
                + self._format_avg_salary(avg_salary) + "\n\n"
                + self._format_high_salary_vacancies(high_salary_vacancies) + "\n\n"
                + self._format_keyword_vacancies("python", keyword_vacancies)
            )
            return report

        except Exception as e:
            return f"Ошибка при формировании отчёта: {e}"
