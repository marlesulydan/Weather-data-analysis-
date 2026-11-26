"""Load the raw weather CSVs, check data quality and build the processed dataset.

Run from the project root with:  python src/data_cleaning.py
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CITIES = ["Astana", "Milan", "Paris", "London"]
START_DATE = "2021-01-01"
END_DATE = "2025-12-31"


def load_raw_data(raw_dir=RAW_DIR):
    """Read the four raw city CSV files and combine them into one DataFrame."""
    frames = [
        pd.read_csv(raw_dir / f"{city.lower()}_daily_2021_2025.csv")
        for city in CITIES
    ]
    return pd.concat(frames, ignore_index=True)


def get_season(month):
    """Return the meteorological season for a month number (1-12)."""
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Spring"
    if month in (6, 7, 8):
        return "Summer"
    return "Autumn"


def clean_weather(df):
    """Convert dates to datetime and add year, month and season columns."""
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    df["season"] = df["month"].apply(get_season)
    return df


def run_quality_checks(df):
    """Return the number of problems found by each check (0 means no problem)."""
    full_range = pd.date_range(START_DATE, END_DATE, freq="D")
    missing_days = sum(
        len(full_range.difference(group["time"]))
        for _, group in df.groupby("city")
    )
    humidity = df["relative_humidity_2m_mean"]

    return pd.Series({
        "missing values": int(df.isna().sum().sum()),
        "duplicate city-date rows": int(df.duplicated(subset=["city", "time"]).sum()),
        "missing days": int(missing_days),
        "mean temp below min temp": int((df["temperature_2m_mean"] < df["temperature_2m_min"]).sum()),
        "mean temp above max temp": int((df["temperature_2m_mean"] > df["temperature_2m_max"]).sum()),
        "rain_sum above precipitation_sum": int((df["rain_sum"] > df["precipitation_sum"]).sum()),
        "negative precipitation": int((df["precipitation_sum"] < 0).sum()),
        "humidity outside 0-100": int(((humidity < 0) | (humidity > 100)).sum()),
    })


def main():
    weather = clean_weather(load_raw_data())

    checks = run_quality_checks(weather)
    print(checks)
    if checks.sum() > 0:
        raise ValueError("Data quality checks failed, see the table above.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "weather_clean.csv"
    weather.to_csv(output_path, index=False)
    print(f"Saved {len(weather)} rows to {output_path}")


if __name__ == "__main__":
    main()