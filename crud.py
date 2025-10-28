"""
CRUD module - defines functions for creating, reading,
updating, and deleting country records in the database.
"""
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session
from models import Country


def create_or_update_country(session: Session, country_data: dict):
    """
    Create or update a country in the database.

    Parameters:
    ----------
        session (Session): Database session.
        country_data (dict): Data for the country to be created or updated.

    Returns:
    -------
        Country: The created or updated country object.
    """
    existing_country = session.query(Country).filter(
        func.lower(Country.name) == func.lower(country_data["name"])
    ).first()

    if existing_country:
        for key, value in country_data.items():
            setattr(existing_country, key, value)
        existing_country.last_refreshed_at = datetime.utcnow()
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        session.refresh(existing_country)
        return existing_country

    new_country = Country(**country_data)
    session.add(new_country)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    session.refresh(new_country)
    return new_country


def get_country_by_name(session: Session, name: str):
    """
    Retrieve a country by its name.

    Parameters:
    ----------
        session (Session): Database session.
        name (str): Name of the country to retrieve.

    Returns:
    -------
        Country: The country object if found, else None.
    """
    return session.query(Country).filter(
        func.lower(Country.name) == func.lower(name)).first()


def get_countries(session: Session,
                  region: str = None,
                  currency_code: str = None,
                  sort_by: str = None,
                  sort_order: str = "asc"):
    """
    Retrieves all countries from the database.

    Parameters:
    ----------
        session (Session): Database session.
        region (str, optional): Filter by region. Defaults to None.
        currency_code (str, optional): Filter by currency code.
                            Defaults to None.
        sort_by (str, optional): Column to sort by. Defaults to None.
        sort_order (str, optional): Sort order, either "asc" or "desc".

    Returns:
    -------
        List[Country]: A list of all countries in the database.
    """
    query = session.query(Country)
    if region:
        query = query.filter(func.lower(Country.region) == func.lower(region))
    if currency_code:
        query = query.filter(func.lower(Country.currency_code) ==
                             func.lower(currency_code))
    if sort_by and hasattr(Country, sort_by):
        if sort_order == "asc":
            query = query.order_by(getattr(Country, sort_by).asc())
        else:
            query = query.order_by(getattr(Country, sort_by).desc())
    return query.all()


def delete_country(session: Session, name: str):
    """
    Deletes a country from the database by its name.

    Parameters:
    ----------
        session (Session): Database session.
        name (str): Name of the country to delete.

    Returns:
    -------
        bool: True if the country was deleted, False if not found.
    """
    country = get_country_by_name(session, name)
    if country:
        session.delete(country)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        return True
    return False


def count_countries(session: Session):
    """
    Counts the total number of countries in the database.

    Parameters:
    ----------
        session (Session): Database session.

    Returns:
    -------
        int: The total number of countries.
    """
    return session.query(Country).count()
