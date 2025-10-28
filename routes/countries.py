"""
Module for Fast API routes that have `/countries` prefix.
"""
import os
from datetime import datetime
from typing import List
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from crud import (delete_country as crud_delete_country,
                  get_countries as crud_get_countries, get_country_by_name)
from db import get_db
from schemas import CountryResponse
from utils import generate_summary_image, _process_single_country_data

router = APIRouter(prefix="/countries", tags=["countries"])

COUNTRIES_API_URL = "https://restcountries.com/v2/all?" \
                     "fields=name,capital,region,population,flag,currencies"
EXCHANGE_API_URL = "https://open.er-api.com/v6/latest/USD"


@router.get("/image", response_class=FileResponse)
def get_summary_image():
    """
    Gets a cached summary image of the countries data.

    Returns:
    -------
        FileResponse: The summary image file.
    """
    image_path = "cache/summary.png"
    if not os.path.exists(image_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error": "Summary image not found"})
    return FileResponse(image_path, media_type="image/png")


@router.post("/refresh", response_model=dict)
def refresh_countries(db: Session = Depends(get_db)):
    """
    Refresh the countries data by fetching from external APIs
    and updating the database.

    Returns:
    -------
        dict: A dictionary containing the status of the refresh operation.

    Raises:
    ------
        HTTPException: If there is an error fetching data
        from the external APIs.
    """
    try:
        countries_response = requests.get(COUNTRIES_API_URL, timeout=15)
        exchange_response = requests.get(EXCHANGE_API_URL, timeout=15)
        countries_response.raise_for_status()
        exchange_response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "External data source unavailable",
                "details": str(e)
            }
        ) from e

    countries_data = countries_response.json()
    exchange_data = exchange_response.json().get("rates", {})
    timestamp = datetime.now().isoformat()

    for country in countries_data:
        _process_single_country_data(db, country, exchange_data)

    try:
        generate_summary_image(db)
    except Exception as e:
        print(f"Error generating summary image: {e}")

    return {
        "message": "Countries refreshed successfully",
        "total_countries": len(countries_data),
        "last_refreshed_at": timestamp
    }


@router.get("", response_model=List[CountryResponse])
def list_countries(
    region: str = None,
    currency: str = None,
    sort: str = None,
    db: Session = Depends(get_db)
):
    """
    Gets a list of countries with optional filters
    & sorting.

    Parameters:
    ----------
        region (str): Filter by region.
        currency (str): Filter by currency code.
        sort (str): Sort query like 'gdp_desc' or 'gdp_asc'.

    Returns:
    -------
        List[CountryResponse]: A list of countries matching the filters.
    """
    sort_by = None
    sort_order = "asc"
    if sort:
        if sort.endswith("_desc"):
            sort_by = sort[:-5]
            sort_order = "desc"
        elif sort.endswith("_asc"):
            sort_by = sort[:-4]
            sort_order = "asc"
        else:
            raise HTTPException(
                status_code=400,
                detail={"error": "Validation failed",
                        "details": {"sort": "must end with _asc or _desc"}}
            )
    countries: list = crud_get_countries(db, region, currency,
                                         sort_by, sort_order)
    return [CountryResponse.from_orm(c) for c in countries]


@router.get("/{name}", response_model=CountryResponse)
def get_country(name: str, db: Session = Depends(get_db)):
    """
    Gets a single country by its name.

    Parameters:
    ----------
        name (str): Name of the country to retrieve.

    Returns:
    -------
        CountryResponse: The country object if found, else raises HTTP 404.

    Raises
    ------
        HTTPException: If the country is not found, raises 404 Not Found.
    """
    country = get_country_by_name(db, name)
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error": "Country not found"})
    return country


@router.delete("/{name}", response_model=dict)
def delete_country_route(name: str, db: Session = Depends(get_db)):
    """
    Deletes a country by its name.

    Parameters:
    ----------
        name (str): Name of the country to delete.

    Returns:
    -------
        dict: A dictionary containing the status of the deletion operation.

    Raises:
    ------
        HTTPException: If the country is not found, raises 404 Not Found.
    """
    deleted = crud_delete_country(db, name)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"error": "Country not found"})
    return {"status": "success",
            "message": f"Country '{name}' deleted successfully"}
