# Weather-Around-The-World-Dashboard
The project will involve Selenium for web scraping, data cleaning, transforming the data into a structured format, storing it in a SQLite database, querying it via command line, and presenting it using Streamlit for interactive visualizations.
## Project Overview

This project collects current weather information for cities around the world from Timeanddate.com. The collected data is cleaned and prepared for later storage, analysis, and visualization.

## Data Collected

The scraper collects:

- City
- Country
- Weather condition
- Local time
- Temperature in Fahrenheit
- Temperature in Celsius
- Source URL
- Date and time the data was collected

## Project Files

- `scrape-weather.py` — scrapes weather information and saves it to `raw_weather.csv`
- `clean-weather.py` — cleans and transforms the raw weather data
- `raw_weather.csv` — original scraped weather data
- `clean_weather.csv` — cleaned weather data
- `country_temperature_summary.csv` — temperature summary by country
- `hot_cities.csv` — cities with temperatures at or above 30 degrees Celsius
- `requirements.txt` — Python packages required by the project

## How to Run the Project

Install the required packages:
```bash
python -m pip install -r requirements.txt
```

Collect the weather data:

```bash
python scrape-weather.py
```

Clean and analyze the collected data:

```bash
python clean-weather.py
```

## Current Progress

The weather scraping and data-cleaning portions are complete. The project currently produces raw, cleaned, summary, and hot-city CSV files. SQLite storage and the Streamlit dashboard will be added during later stages of the capstone project.