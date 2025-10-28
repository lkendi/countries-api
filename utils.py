"""
Utility functions module
"""
import os
import random
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy.orm import Session
from models import Country
from crud import create_or_update_country


def generate_summary_image(db: Session, image_path="cache/summary.png"):
    """
    Generates a summary image of the countries data
    and saves it to the specified path.

    Parameters:
    ----------
        countries_data (list): List of country data dictionaries.
        image_path (str): Path where the summary image will be saved.

    Returns:
    -------
        str: Path to the generated summary image.
    """
    if not os.path.exists("cache"):
        os.makedirs("cache")

    total_countries = db.query(Country).count()
    top_countries = (
        db.query(Country)
        .filter(Country.estimated_gdp.isnot(None))
        .order_by(Country.estimated_gdp.desc())
        .limit(5)
        .all()
        )

    last_refresh = (
        db.query(Country.last_refreshed_at)
        .order_by(Country.last_refreshed_at.desc())
        .first()
    )

    last_refresh = (
        last_refresh[0].isoformat() if last_refresh else "N/A"
    )

    img = Image.new("RGB", (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_text = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    draw.text((20, 20), "Country Summary",
              fill="black", font=font_title)
    draw.text((20, 80), f"Total Countries: {total_countries}",
              fill="black", font=font_text)
    draw.text((20, 120), f"Last Refreshed: {last_refresh}",
              fill="black", font=font_text)
    draw.text((20, 170), "Top 5 by Estimated GDP:",
              fill="black", font=font_text)

    y = 200
    for idx, country in enumerate(top_countries, start=1):
        text = f"{idx}. {country.name} — {round(
            country.estimated_gdp or 0, 2):,}"
        draw.text((40, y), text, fill="black", font=font_text)
        y += 30

    img.save(image_path)
    return image_path


def _process_single_country_data(db: Session,
                                 country: dict,
                                 exchange_data: dict):
    """
    Helper function to process and store data for a single country.

    Parameters:
    ----------
        db (Session): Database session.
        country (dict): Country data dictionary.
        exchange_data (dict): Exchange rate data dictionary.

    Returns:
    -------
        None
    """
    country_name = country.get("name")
    capital = country.get("capital")
    region = country.get("region")
    population = country.get("population")
    flag_url = country.get("flag")
    currencies = country.get("currencies", [])
    currency_code = currencies[0].get("code") if currencies else None

    exchange_rate = (exchange_data.get(currency_code)
                     if currency_code in exchange_data else None)
    multiplier = random.uniform(1000, 2000)
    estimated_gdp = ((population * multiplier) / exchange_rate
                     if exchange_rate else 0)

    country_dict = {
        "name": country_name,
        "capital": capital,
        "region": region,
        "population": population or 0,
        "currency_code": currency_code,
        "exchange_rate": exchange_rate,
        "estimated_gdp": estimated_gdp,
        "flag_url": flag_url,
        "last_refreshed_at": datetime.now()
    }

    create_or_update_country(db, country_dict)
