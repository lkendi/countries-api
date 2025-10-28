# Countries API

A RESTful API for fetching, caching, and serving country data, including currency exchange rates and estimated GDP.

## Features

- Fetches country data from [RestCountries](https://restcountries.com/).
- Fetches currency exchange rates from [ExchangeRate-API](https://www.exchangerate-api.com/).
- Caches the combined data in a MySQL database.
- Provides CRUD endpoints to manage country data.
- Generates and serves a dynamic summary image of the cached data.

## Setup and Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd countries-api
```

### 2. Create and Activate Virtual Environment

```bash
# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a file named `.env` in the project root and add the following line. Replace the placeholder with your actual MySQL connection string.

```env
DATABASE_URL="mysql+pymysql://user:password@host:port/database"
```

### 5. Run the Application

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Interactive Documentation

Access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs` once the application is running.

### Refresh Data

- **`POST /countries/refresh`**
  - **Description:** Fetches the latest data from external APIs, updates the database, and generates a new summary image.
  - **Success Response (200):**
    ```json
    {
      "message": "Countries refreshed successfully",
      "total_countries": 250,
      "last_refreshed_at": "2025-10-28T12:00:00.000Z"
    }
    ```
  - **Error Response (503):** If external APIs are unavailable.

### Get Countries

- **`GET /countries`**
  - **Description:** Retrieves a list of all countries. Supports filtering and sorting.
  - **Query Parameters:**
    - `region` (str): Filter by region (e.g., `Africa`).
    - `currency` (str): Filter by currency code (e.g., `NGN`).
    - `sort` (str): Sort by GDP (e.g., `gdp_desc` or `gdp_asc`).
  - **Success Response (200):**
    ```json
    [
      {
        "id": 1,
        "name": "Nigeria",
        "capital": "Abuja",
        "region": "Africa",
        "population": 206139589,
        "currency_code": "NGN",
        "exchange_rate": 1600.23,
        "estimated_gdp": 25767448125.2,
        "flag_url": "https://flagcdn.com/ng.svg",
        "last_refreshed_at": "2025-10-28T12:00:00.000Z"
      }
    ]
    ```

- **`GET /countries/{name}`**
  - **Description:** Retrieves a single country by its name.
  - **Success Response (200):** A single country object.
  - **Error Response (404):** If the country is not found.

### Delete Country

- **`DELETE /countries/{name}`**
  - **Description:** Deletes a country record from the database.
  - **Success Response (200):**
    ```json
    {
      "status": "success",
      "message": "Country 'Nigeria' deleted successfully"
    }
    ```
  - **Error Response (404):** If the country is not found.

### Status & Summary Image

- **`GET /status`**
  - **Description:** Shows the total number of countries and the last refresh timestamp.
  - **Success Response (200):**
    ```json
    {
      "total_countries": 250,
      "last_refreshed_at": "2025-10-28T12:00:00.000Z"
    }
    ```

- **`GET /countries/image`**
  - **Description:** Serves the generated summary image (`summary.png`).
  - **Success Response (200):** An image file (`image/png`).
  - **Error Response (404):** If the summary image has not been generated yet.
