"""
Status Route Module
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import Country
from db import get_db
from crud import count_countries

router = APIRouter(tags=["status"])


@router.get("/status", response_model=dict)
def get_status(db: Session = Depends(get_db)):
    """
    Gets total number of countries in the database
    and the last refreshed timestamp.

    Parameters:
    ----------
        db (Session): Database session.

    Returns:
    -------
        dict: A dictionary containing the status of the API.
    """
    total_countries = count_countries(db)
    last_refresh = db.query(Country.last_refreshed_at).order_by(
        Country.last_refreshed_at.desc()).first()
    return {
        "total_countries": total_countries,
        "last_refreshed_at": last_refresh[0].isoformat()
        if last_refresh else None
    }
