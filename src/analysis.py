"""Statistical analysis functions for the weather dataset.

Every function takes the cleaned DataFrame and returns a table (no printing or
plotting here). Run from the project root with:  python src/analysis.py
"""

import pandas as pd

from data_cleaning import CITIES, PROCESSED_DIR

CITY_ORDER = CITIES
SEASON_ORDER = ["Winter", "Spring", "Summer", "Autumn"]
RAIN_THRESHOLDS_MM = [0.1, 1.0, 5.0]
STRONG_WIND_KMH = 40
CORRELATION_VARIABLES = [
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "relative_humidity_2m_mean",
]


def load_clean_data(path=PROCESSED_DIR / "weather_clean.csv"):
    """Read the processed dataset; dates are parsed as datetimes."""
    return pd.read_csv(path, parse_dates=["time"])


def annual_mean(df, column):
    """Mean of a column per year (rows) and city (columns)."""
    table = df.groupby(["city", "year"])[column].mean().unstack("city")
    return table.loc[:, CITY_ORDER]


def annual_total(df, column):
    """Sum of a column per year (rows) and city (columns)."""
    table = df.groupby(["city", "year"])[column].sum().unstack("city")
    return table.loc[:, CITY_ORDER]


def temperature_variation(df):
    """Three measures of temperature variation per city (Q2)."""
    daily = df.groupby("city")["temperature_2m_mean"]
    monthly = df.groupby(["city", "month"])["temperature_2m_mean"].mean()
    by_city = monthly.groupby("city")
    result = pd.DataFrame({
        "std_c": daily.std(),
        "range_c": daily.max() - daily.min(),
        "annual_amplitude_c": by_city.max() - by_city.min(),
    })
    return result.loc[CITY_ORDER]


def seasonal_mean(df, column):
    """Mean of a column per city (rows) and meteorological season (columns)."""
    table = df.groupby(["city", "season"])[column].mean().unstack("season")
    return table.loc[CITY_ORDER, SEASON_ORDER]


def seasonal_precipitation(df):
    """Average precipitation total per season and year, in mm (Q4)."""
    n_years = df["year"].nunique()
    table = (
        df.groupby(["city", "season"])["precipitation_sum"].sum()
        .div(n_years)
        .unstack("season")
    )
    return table.loc[CITY_ORDER, SEASON_ORDER]


def rainy_days_by_year(df, threshold_mm=1.0):
    """Number of days with rain_sum >= threshold, per year and city (Q5)."""
    is_rainy = df["rain_sum"] >= threshold_mm
    table = is_rainy.groupby([df["city"], df["year"]]).sum().unstack("city")
    return table.loc[:, CITY_ORDER]


def rainy_days_per_year(df, thresholds=RAIN_THRESHOLDS_MM):
    """Average rainy days per year for several thresholds (Q5)."""
    n_years = df["year"].nunique()
    table = pd.DataFrame({
        f"rain_sum >= {t} mm": (df["rain_sum"] >= t).groupby(df["city"]).sum() / n_years
        for t in thresholds
    })
    return table.loc[CITY_ORDER]


def overall_correlation(df):
    """Pearson and Spearman correlation of temperature and precipitation (Q6).

    Spearman is Pearson computed on ranks, so no extra library is needed.
    """
    rows = {}
    for city, group in df.groupby("city"):
        temp = group["temperature_2m_mean"]
        precip = group["precipitation_sum"]
        rows[city] = {
            "pearson": temp.corr(precip),
            "spearman": temp.rank().corr(precip.rank()),
        }
    return pd.DataFrame(rows).T.loc[CITY_ORDER]


def seasonal_correlation(df):
    """Pearson correlation of temperature and precipitation per city and season."""
    rows = {}
    for (city, season), group in df.groupby(["city", "season"]):
        rows[(city, season)] = group["temperature_2m_mean"].corr(group["precipitation_sum"])
    return pd.Series(rows).unstack().loc[CITY_ORDER, SEASON_ORDER]


def variable_correlation(df, city, variables=CORRELATION_VARIABLES):
    """Correlation matrix between weather variables for one city."""
    return df.loc[df["city"] == city, variables].corr()


def wind_statistics(df, strong_wind_kmh=STRONG_WIND_KMH):
    """Wind statistics per city (Q7), using daily maximum 10 m wind speed."""
    n_years = df["year"].nunique()
    wind = df.groupby("city")["wind_speed_10m_max"]
    stats = wind.agg(
        mean="mean",
        median="median",
        p95=lambda s: s.quantile(0.95),
        max="max",
    )
    strong_days = (df["wind_speed_10m_max"] >= strong_wind_kmh).groupby(df["city"]).sum()
    stats[f"days_ge_{strong_wind_kmh}_kmh_per_year"] = strong_days / n_years
    return stats.loc[CITY_ORDER]


def city_summary(df):
    """One row per city with the main indicators."""
    table = pd.DataFrame({
        "mean_temp_c": df.groupby("city")["temperature_2m_mean"].mean(),
        "temp_std_c": df.groupby("city")["temperature_2m_mean"].std(),
        "winter_temp_c": seasonal_mean(df, "temperature_2m_mean")["Winter"],
        "summer_temp_c": seasonal_mean(df, "temperature_2m_mean")["Summer"],
        "annual_precip_mm": annual_total(df, "precipitation_sum").mean(),
        "rainy_days_ge_1mm": rainy_days_by_year(df, 1.0).mean(),
        "mean_humidity_pct": df.groupby("city")["relative_humidity_2m_mean"].mean(),
        "mean_wind_kmh": df.groupby("city")["wind_speed_10m_max"].mean(),
    })
    return table.loc[CITY_ORDER]


def astana_vs_europe(df):
    """Compare Astana with the simple mean of Milan, Paris and London (Q8)."""
    summary = city_summary(df)
    comparison = pd.DataFrame({
        "Astana": summary.loc["Astana"],
        "European mean": summary.drop(index="Astana").mean(),
    })
    comparison["Astana minus Europe"] = comparison["Astana"] - comparison["European mean"]
    return comparison


def main():
    df = load_clean_data()
    pd.set_option("display.width", 120)

    results = {
        "Mean annual temperature (Q1)": annual_mean(df, "temperature_2m_mean").mean(),
        "Temperature variation (Q2)": temperature_variation(df),
        "Mean annual precipitation, mm (Q3)": annual_total(df, "precipitation_sum").mean(),
        "Seasonal mean temperature (Q4)": seasonal_mean(df, "temperature_2m_mean"),
        "Rainy days per year (Q5)": rainy_days_per_year(df),
        "Temperature vs precipitation, all days (Q6)": overall_correlation(df),
        "Temperature vs precipitation by season (Q6)": seasonal_correlation(df),
        "Wind statistics (Q7)": wind_statistics(df),
        "Astana vs European mean (Q8)": astana_vs_europe(df),
    }
    for title, table in results.items():
        print(f"\n=== {title} ===")
        print(table.round(2))


if __name__ == "__main__":
    main()