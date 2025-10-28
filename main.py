"""
Main application file

Initializes the FastAPI application, sets up the database,
and includes the routers for countries and status endpoints.
Also handles exceptions and provides custom error responses.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, \
        HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from db import Base, engine
from routes.countries import router as countries_router
from routes.status import router as status_router


@asynccontextmanager
async def lifespan():
    """
    Lifespan event handler for the FastAPI application.
    Creates the db tables if they don't exist.
    Yields control to the application, allowing it to run.
    Also handles shutdown events.
    """
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI()

app.include_router(countries_router)
app.include_router(status_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
            _request: Request,
            exc: RequestValidationError):
    """
    Handles validation exceptions by formatting the error messages
    into a JSON response.

    Parameters
    ----------
    request : Request
        The request that caused the exception.
    exc : RequestValidationError
        The validation exception that was raised.

    Returns
    -------
    JSONResponse
        A JSON response containing the error messages.
    """
    errors = {}
    for err in exc.errors():
        field = err.get("loc")[-1]
        msg = err.get("msg")
        errors[field] = msg.replace("Field required", "is required")
    return JSONResponse(
        status_code=400,
        content={"error": "Validation failed", "details": errors},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException):
    """
    Handles Starlette HTTP exceptions by formatting the error messages
    into a JSON response.

    Parameters
    ----------
    request : Request
        The request that caused the exception.
    exc : StarletteHTTPException
        The HTTP exception that was raised.

    Returns
    -------
    JSONResponse
        A JSON response containing the error messages.
    """
    detail = exc.detail if isinstance(
        exc.detail, dict) else {"error": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content=detail)


@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception):
    """
    Handles any exceptions that are not handled by other exception handlers.

    Parameters
    ----------
    request : Request
        The request that caused the exception.
    exc : Exception
        The exception that was raised.

    Returns
    -------
    JSONResponse
        A JSON response containing the error messages.
    """
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)},
    )
