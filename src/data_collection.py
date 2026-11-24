"""Download daily historical weather data from Open-Meteo for four cities.

The raw data is saved as one CSV file per city in data/raw/.
Run from the project root with:  python src/data_collection.py
"""

from pathlib import Path

import pandas as pd
import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive"
START_DATE = "2021-01-01"
END_DATE = "2025-12-31"

# City name -> (latitude, longitude)
CITIES = {
    "Astana": (51.1694, 71.4491),
    "Milan": (45.4642, 9.1900),
    "Paris": (48.8566, 2.3522),
    "London": (51.5074, -0.1278),
}

DAILY_VARIABLES = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rain_sum",
    "wind_speed_10m_max",
    "relative_humidity_2m_mean",
]

# Project root = the parent of the "src" folder this file lives in
RAW_DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch_city_data(city, latitude, longitude):
    """Request daily weather data for one city and return it as a DataFrame."""
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": DAILY_VARIABLES,
        "timezone": "auto",
    }
    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()  # stop with an error if the request failed

    data = response.json()
    df = pd.DataFrame(data["daily"])
    df.insert(0, "city", city)  # add a "city" column as the first column
    return df


def save_raw_csv(df, city):
    """Save a DataFrame to data/raw/<city>_daily_2021_2025.csv."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = RAW_DATA_DIR / f"{city.lower()}_daily_2021_2025.csv"
    df.to_csv(file_path, index=False)
    return file_path


def main():
    for city, (latitude, longitude) in CITIES.items():
        df = fetch_city_data(city, latitude, longitude)
        file_path = save_raw_csv(df, city)
        print(f"{city}: {len(df)} rows saved to {file_path}")


if __name__ == "__main__":
    main()