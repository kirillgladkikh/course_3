
from config import config
from src.utils_course_3 import get_hh_data, create_database, save_data_to_database


def main():
    employers_ids = [
        '1336085',  # Авилхан Айболат
        '4417413',  # SМMPro
        '11709856',  # Таржакаев
        '967285',  # Футбольный клуб Кайрат
        '763400',  # 21vek.by
        '5031522',  # Autodata
        '1475584',  # Kufar
        '155987',  # КазГЮУ, АО
        '1245405',  # Bereke Bank
        '12468554',  # Форэва Бай
    ]

    params = config()

    # data = get_hh_data(employers_ids)
    create_database('course3', params)
    # save_data_to_database(data, 'course3', params)


if __name__ == '__main__':
    main()