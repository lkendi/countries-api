"""
Schema for the country model
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CountryBase(BaseModel):
    """
    Base schema defining shared attributes for country data
    used both by external API and db interactions.

    Attributes:
    -----------
    id (Optional[int]): Unique identifier for the country
    name (str): Name of the country
    capital (Optional[str]): Capital city of the country
    region (Optional[str]): Region where the country is located
    population (int): Population of the country
    currency_code (Optional[str]): Currency code of the country
    exchange_rate (Optional[float]): Exchange rate of the
                        country's currency compared to USD
    estimated_gdp (Optional[float]): Estimated GDP of the country
    flag_url (Optional[str]): URL of the country's flag image
    """
    id: Optional[int] = Field(None)
    name: str = Field(...)
    capital: Optional[str] = Field(None)
    region: Optional[str] = Field(None)
    population: int = Field(...)
    currency_code: Optional[str] = Field(None)
    exchange_rate: Optional[float] = Field(None)
    estimated_gdp: Optional[float] = Field(None)
    flag_url: Optional[str] = Field(None)


class CountryResponse(CountryBase):
    """
    Response model for country data
    """
    id: int
    last_refreshed_at: datetime
    model_config = {"from_attributes": True}
