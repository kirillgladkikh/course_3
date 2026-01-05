
from config import config
from src.utils_course_3 import get_hh_data, create_database, save_data_to_database


def main():
    employers_ids = [
        '1740',  # Яндекс
        '67611',  # Тензор
        '4614421',  # RedLab
        '727029',  # PravoTech
        '2300703',  # Открытая мобильная платформа
        '819979',  # SkillStaff
        '1993194',  # YADRO
        '894410',  # РТЛабс
        '1473866',  # ООО Сбербанк-Сервис
        '1057',  # Лаборатория Касперского
    ]

    params = config()

    # data = get_hh_data(employers_ids)
    create_database('course3', params)
    save_data_to_database(data, 'course3', params)


if __name__ == '__main__':
    main()