# Weather Data Analysis: Astana, Milan, Paris and London (2021-2025)

Individual project for the course *Coding for Data Science and Data Management*, University of Milan (UNIMI), academic year 2026-2027.

The project collects daily historical weather data for four cities, cleans it, analyses it with Python and compares the climates of the cities.

## Research questions

1. Which city has the highest average annual temperature?
2. Which city experiences the greatest temperature variation?
3. Which city receives the highest amount of precipitation?
4. How do seasonal temperature patterns differ between the four cities?
5. Which city experiences the most rainy days?
6. Is there a relationship between temperature and precipitation?
7. Which city experiences the strongest winds?
8. How does Astana's climate differ from the European cities?

## Data

- **Source:** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) (default "Best Match" model selection). Weather data by Open-Meteo.com; check the terms on the Open-Meteo website before reusing the data.
- **Important:** the values are *reanalysis* estimates (model output that combines many observation types), not measurements from a single weather station.
- **Period:** 2021-01-01 to 2025-12-31, daily values, 1826 rows per city.
- **Variables:** mean/max/min temperature at 2 m (°C), precipitation sum (mm, includes snow), rain sum (mm), maximum 10 m wind speed (km/h, not gusts), mean relative humidity at 2 m (%).
- **Cities and coordinates:** Astana (51.1694, 71.4491), Milan (45.4642, 9.1900), Paris (48.8566, 2.3522), London (51.5074, -0.1278).

## Data licence and citation

Weather data by [Open-Meteo.com](https://open-meteo.com/). The API data are offered under the [Creative Commons Attribution 4.0 (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) licence, and the API is free for non-commercial use; this is a non-commercial university project.

Changes made to the data: the raw files in `data/raw/` are the daily values as returned by the API with one added `city` column; `data/processed/weather_clean.csv` additionally contains year, month and season columns.

Citation: Zippenfenig, P. (2023). Open-Meteo.com Weather API [Computer software]. Zenodo. https://doi.org/10.5281/ZENODO.7970649

## Project structure

```
README.md
requirements.txt
data/
  raw/                 one CSV per city, as downloaded
  processed/           weather_clean.csv (all cities, dates parsed, year/month/season added)
notebooks/
  weather_analysis.ipynb   methodology, results and conclusions
src/
  data_collection.py   downloads the raw data
  data_cleaning.py     loads, cleans and quality-checks the data
  analysis.py          statistical functions for the research questions
  visualization.py     plotting functions, saves figures
outputs/
  figures/             PNG figures produced by visualization.py
```

## How to run

Developed and run with Python 3.14.0 on Windows.

```
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

python src/data_collection.py   # optional: re-downloads the raw data (needs internet)
python src/data_cleaning.py     # builds data/processed/weather_clean.csv
python src/analysis.py          # prints the result tables
python src/visualization.py     # saves the figures to outputs/figures/
jupyter notebook notebooks/weather_analysis.ipynb
```

The raw CSV files are included in the repository, so `data_collection.py` does not have to be run again.

## Main findings (2021-2025)

Details, tables and figures are in the notebook.

1. Milan has the highest mean temperature (14.4 °C), then Paris (12.5), London (11.7) and Astana (4.8); the order is the same in every year.
2. Astana varies most (standard deviation 13.6 °C against 5.7-8.1 °C), mainly because of the seasonal cycle.
3. Milan receives the most precipitation (about 1295 mm per year), then Paris (862), London (747) and Astana (434).
4. Astana's winters are about 17 °C colder than the European cities, but its summers are similar to Paris.
5. The city with the most rainy days depends on the threshold: London (>= 0.1 mm), Paris (>= 1 mm), Milan (>= 5 mm); Astana has the fewest.
6. Over all days temperature and precipitation are almost uncorrelated; within seasons the correlation is positive in winter and negative in summer.
7. London has the strongest winds (daily maximum wind speed), followed by Astana, Paris and Milan.
8. Astana is colder, much drier and has a larger seasonal range than Milan, Paris and London.

## Limitations

- Only five years, so single years or events can dominate averages (for example May 2024 in Milan).
- Reanalysis data: model-based, not station records; absolute precipitation totals should be read with care.
- Daily boundaries use a fixed UTC offset per request (daylight saving is ignored).
- Wind is the daily maximum of the regular 10 m wind speed, not gusts.
- Correlations are descriptive and do not show causes.

## Status

Implemented and run: data collection, cleaning with quality checks, statistics for all eight questions (with a NumPy cross-check of the main calculations), figures, and the notebook with conclusions. Not yet done: the presentation and oral-exam preparation.