"""Plotting functions for the weather analysis.

Each function takes the cleaned DataFrame and returns a Matplotlib figure.
Run from the project root to save all figures to outputs/figures/:
    python src/visualization.py
"""

import matplotlib.pyplot as plt
import seaborn as sns

from analysis import (
    CITY_ORDER,
    SEASON_ORDER,
    load_clean_data,
    monthly_precipitation,
    monthly_temperature,
    seasonal_correlation,
    seasonal_mean,
    variable_correlation,
)
from data_cleaning import PROJECT_ROOT

FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
CITY_COLORS = dict(zip(CITY_ORDER, sns.color_palette("tab10", len(CITY_ORDER))))
VARIABLE_LABELS = ["Temperature", "Precipitation", "Wind speed", "Humidity"]

sns.set_theme(style="whitegrid")


def plot_temperature_distribution(df):
    """Histogram with density curve of daily mean temperature, per city."""
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(
        data=df, x="temperature_2m_mean", hue="city", hue_order=CITY_ORDER,
        palette=CITY_COLORS, kde=True, element="step", stat="density", ax=ax,
    )
    ax.set_title("Distribution of daily mean temperature, 2021-2025")
    ax.set_xlabel("Daily mean temperature (°C)")
    ax.set_ylabel("Density")
    plt.close(fig)
    return fig


def plot_monthly_temperature(df):
    """Mean daily temperature for each calendar month, per city."""
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=monthly_temperature(df), x="month", y="temperature_2m_mean",
        hue="city", hue_order=CITY_ORDER, palette=CITY_COLORS, marker="o", ax=ax,
    )
    ax.set_xticks(range(1, 13))
    ax.set_title("Mean daily temperature by month, 2021-2025")
    ax.set_xlabel("Month")
    ax.set_ylabel("Mean daily temperature (°C)")
    plt.close(fig)
    return fig


def plot_monthly_precipitation(df):
    """Average monthly precipitation total, per city."""
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(
        data=monthly_precipitation(df), x="month", y="avg_monthly_precip_mm",
        hue="city", hue_order=CITY_ORDER, palette=CITY_COLORS, ax=ax,
    )
    ax.set_title("Average monthly precipitation, 2021-2025")
    ax.set_xlabel("Month")
    ax.set_ylabel("Precipitation (mm per month)")
    plt.close(fig)
    return fig


def plot_temperature_boxplot(df):
    """Boxplot of daily mean temperature, per city."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=df, x="city", y="temperature_2m_mean", order=CITY_ORDER,
        hue="city", palette=CITY_COLORS, legend=False, ax=ax,
    )
    ax.set_title("Daily mean temperature by city, 2021-2025")
    ax.set_xlabel("City")
    ax.set_ylabel("Daily mean temperature (°C)")
    plt.close(fig)
    return fig


def plot_wind_boxplot(df):
    """Boxplot of daily maximum 10 m wind speed, per city."""
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(
        data=df, x="city", y="wind_speed_10m_max", order=CITY_ORDER,
        hue="city", palette=CITY_COLORS, legend=False, ax=ax,
    )
    ax.set_title("Daily maximum wind speed by city, 2021-2025")
    ax.set_xlabel("City")
    ax.set_ylabel("Daily maximum wind speed (km/h)")
    plt.close(fig)
    return fig


def plot_seasonal_temperature(df):
    """Mean daily temperature per meteorological season, per city."""
    table = (
        seasonal_mean(df, "temperature_2m_mean")
        .reset_index()
        .melt(id_vars="city", var_name="season", value_name="temperature_c")
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(
        data=table, x="season", y="temperature_c", order=SEASON_ORDER,
        hue="city", hue_order=CITY_ORDER, palette=CITY_COLORS, ax=ax,
    )
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Mean daily temperature by season, 2021-2025")
    ax.set_xlabel("Season")
    ax.set_ylabel("Mean daily temperature (°C)")
    plt.close(fig)
    return fig


def plot_seasonal_correlation_heatmap(df):
    """Heatmap of the temperature-precipitation correlation per city and season."""
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.heatmap(
        seasonal_correlation(df), annot=True, fmt=".2f", cmap="coolwarm",
        center=0, vmin=-0.5, vmax=0.5,
        cbar_kws={"label": "Pearson correlation"}, ax=ax,
    )
    ax.set_title("Temperature vs precipitation: correlation by season")
    ax.set_xlabel("Season")
    ax.set_ylabel("City")
    plt.close(fig)
    return fig


def plot_variable_correlation_heatmaps(df):
    """One correlation heatmap per city for the four main weather variables."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    for ax, city in zip(axes.flat, CITY_ORDER):
        corr = variable_correlation(df, city)
        corr.index = VARIABLE_LABELS
        corr.columns = VARIABLE_LABELS
        sns.heatmap(
            corr, annot=True, fmt=".2f", cmap="coolwarm",
            center=0, vmin=-1, vmax=1, ax=ax, cbar=False,
        )
        ax.set_title(city)
    fig.suptitle(
        "Correlation between daily weather variables, 2021-2025 (all days, scale -1 to +1)"
    )
    fig.tight_layout()
    plt.close(fig)
    return fig


def save_figure(fig, filename, figures_dir=FIGURES_DIR):
    """Save a figure as PNG in the figures folder and return the file path."""
    figures_dir.mkdir(parents=True, exist_ok=True)
    path = figures_dir / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    return path


def main():
    plt.switch_backend("Agg")  # draw to files, no windows
    df = load_clean_data()

    figures = {
        "temperature_distribution.png": plot_temperature_distribution(df),
        "monthly_temperature.png": plot_monthly_temperature(df),
        "monthly_precipitation.png": plot_monthly_precipitation(df),
        "temperature_boxplot.png": plot_temperature_boxplot(df),
        "wind_boxplot.png": plot_wind_boxplot(df),
        "seasonal_temperature.png": plot_seasonal_temperature(df),
        "seasonal_correlation_heatmap.png": plot_seasonal_correlation_heatmap(df),
        "variable_correlation_heatmaps.png": plot_variable_correlation_heatmaps(df),
    }
    for filename, fig in figures.items():
        print("Saved", save_figure(fig, filename))


if __name__ == "__main__":
    main()