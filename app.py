import aiohttp
import asyncio
import argparse
import logging
from decouple import config

from db import init_db, SessionLocal, save_weather_data
from utils import export_to_excel

API_KEY = config('API_KEY')
BASE_URL = 'http://api.weatherapi.com/v1/current.json'
LOCATION = '55.687736,37.368748'
LANGUAGE = 'ru'

WIND_DIRECTION_MAP = {
    'N': 'С', 'NNE': 'ССВ', 'NE': 'СВ', 'ENE': 'ВСВ',
    'E': 'В', 'ESE': 'ВЮВ', 'SE': 'ЮВ', 'SSE': 'ЮЮВ',
    'S': 'Ю', 'SSW': 'ЮЮЗ', 'SW': 'ЮЗ', 'WSW': 'ЗЮЗ',
    'W': 'З', 'WNW': 'ЗСЗ', 'NW': 'СЗ', 'NNW': 'ССЗ'
}


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - '
                                               '%(message)s')


async def fetch_weather_data():
    """
    Асинхронная функция для запроса данных о погоде и записи их в базу данных.
    Запрос повторяется каждые 3 минуты.
    """
    while True:
        params = {
            'key': API_KEY,
            'q': LOCATION,
            'lang': LANGUAGE
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(BASE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        current = data.get('current', {})
                        temperature = current.get('temp_c')
                        wind_speed = round(current.get('wind_kph') / 3.6, 2)
                        wind_direction = current.get('wind_dir')
                        pressure = round(
                            current.get('pressure_mb') * 0.75006, 2
                        )
                        precipitation = current.get('precip_mm')

                        wind_direction_ru = WIND_DIRECTION_MAP.get(
                            wind_direction, wind_direction
                        )

                        precipitation_type = None
                        if precipitation > 0:
                            precipitation_type = current.get(
                                'condition', {}
                            ).get('text')

                        logging.info(f"Температура: {temperature} °C")
                        logging.info(
                            f"Скорость ветра: {wind_speed} м/с, Направление:"
                            f" {wind_direction_ru}")
                        logging.info(f"Давление: {pressure} мм рт. ст.")
                        logging.info(f"Осадки: {precipitation} мм")
                        if precipitation > 0:
                            logging.info(f"Тип осадков: {precipitation_type}")

                        async with SessionLocal() as db_session:
                            await save_weather_data(
                                db_session,
                                temperature=temperature,
                                pressure=pressure,
                                wind_speed=wind_speed,
                                wind_direction=wind_direction_ru,
                                precipitation=precipitation,
                                precipitation_type=precipitation_type
                            )
                    else:
                        logging.error(f"Ошибка получения данных: "
                                      f"{response.status}")
            except Exception as e:
                logging.error(f"Ошибка запроса: {str(e)}")

        await asyncio.sleep(60)


async def main():
    """
    Основная функция программы, которая инициализирует базу данных и
    выполняет запрос данных о погоде или экспорт данных в Excel.
    """
    parser = argparse.ArgumentParser(description="Программа для работы с "
                                                 "погодой")
    parser.add_argument('--export', action='store_true',
                        help="Экспорт данных в Excel")

    args = parser.parse_args()

    await init_db()
    if args.export:
        await export_to_excel()
    else:
        await fetch_weather_data()


if __name__ == "__main__":
    asyncio.run(main())

