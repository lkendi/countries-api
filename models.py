"""
Country model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from db import Base


class Country(Base):
    """
    Model that defines a country
    (as stored in the database)

    Atributes:
    ----------
    id (int): Country id
    name (str): Country name
    capital (str): Country capital
    region (str): Country region
    population (int): Country population
    currency_code (str): Country currency code
    exchange_rate (float): Country exchange rate
    estimated_gdp (float): Country estimates gdp
    flag_url (str): Country flag url
    last_refreshed_at (datetime): Country last refreshed at
    """

    __tablename__ = "tb_countries"

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    name = Column(String(100), index=True, unique=True, nullable=False)
    capital = Column(String(100), nullable=True)
    region = Column(String(50), nullable=True)
    population = Column(Integer, nullable=False)
    currency_code = Column(String(10), nullable=True)
    exchange_rate = Column(Float, nullable=True)
    estimated_gdp = Column(Float, nullable=True)
    flag_url = Column(String(255), nullable=True)
    last_refreshed_at = Column(DateTime,
                               default=datetime.now,
                               onupdate=datetime.now)
