from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./weather_data.db"

engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()


class WeatherData(Base):
    """Модель данных для хранения информации о погоде"""

    __tablename__ = 'weather'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    temperature = Column(Float)
    pressure = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(String)
    precipitation = Column(Float)
    precipitation_type = Column(String)


async def init_db():
    """Инициализирует базу данных и создаёт таблицу weather, если её ещё нет"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def save_weather_data(session, temperature, pressure, wind_speed,
                            wind_direction, precipitation, precipitation_type):
    """Сохраняет данные о погоде в базу данных"""
    new_data = WeatherData(
        temperature=temperature,
        pressure=pressure,
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        precipitation=precipitation,
        precipitation_type=precipitation_type
    )

    session.add(new_data)
    await session.commit()
