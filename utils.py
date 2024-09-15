import openpyxl
from sqlalchemy.future import select
from db import WeatherData, SessionLocal
import logging


async def export_to_excel():
    """Экспортирует последние 10 записей из базы данных в Excel-файл"""
    async with SessionLocal() as session:
        result = await session.execute(
            select(WeatherData).order_by(WeatherData.id.desc()).limit(10))
        records = result.scalars().all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Weather Data"

    sheet.append(["ID", "Время", "Температура (°C)", "Давление (мм рт. ст.)",
                  "Скорость ветра (м/с)", "Направление ветра",
                  "Осадки (мм)", "Тип осадков"])

    for record in records:
        sheet.append([
            record.id,
            record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            record.temperature,
            record.pressure,
            record.wind_speed,
            record.wind_direction,
            record.precipitation,
            record.precipitation_type or "Нет"
        ])

    workbook.save("weather_data.xlsx")
    logging.info("Данные успешно экспортированы в weather_data.xlsx")
