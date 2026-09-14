# Pandas cleaning: clean and transform the raw weather data

import pandas as pd

weather_df = pd.read_csv("raw_weather.csv")

print("Raw data:")
print(weather_df.head())

print("\nDataFrame information:")
weather_df.info()

print("\nMissing values before cleaning:")
print(weather_df.isna().sum())

print("\nDuplicate rows before cleaning:")
print(weather_df.duplicated().sum())

# Rename columns by their original names so CSV column order does not matter.
weather_df.rename(
    columns={
        "City": "city",
        "Condition": "condition",
        "Local-Time": "local_time",
        "Source-URL": "source_url",
        "Temperature": "temperature",
        "Scraped-At": "scraped_at",
    },
    inplace=True,
)

# Remove extra spaces from text columns
text_columns = [
    "city",
    "condition",
    "local_time",
    "source_url",
    "temperature"
]

for column in text_columns:
    weather_df[column] = weather_df[column].str.strip()

# Convert empty strings into missing values
weather_df.replace("", pd.NA, inplace=True)

# Handle missing city and condition values
weather_df["city"] = weather_df["city"].fillna("Unknown")
weather_df["condition"] = weather_df["condition"].fillna("Unknown")

# Remove duplicate records
weather_df.drop_duplicates(inplace=True)

# Extract the numeric Fahrenheit temperature
weather_df["temperature_f"] = pd.to_numeric(
    weather_df["temperature"].str.extract(r"(-?\d+)")[0],
    errors="coerce"
)

# Convert Fahrenheit to Celsius
weather_df["temperature_c"] = (
    (weather_df["temperature_f"] - 32) * 5 / 9
).round(1)

# Extract the country from each source URL
weather_df["country"] = weather_df["source_url"].str.extract(
    r"/weather/([^/]+)/"
)[0]

weather_df["country"] = weather_df["country"].fillna("Unknown")

# Convert the scrape timestamp into a datetime data type
weather_df["scraped_at"] = pd.to_datetime(
    weather_df["scraped_at"],
    errors="coerce",
    utc=True
)

# Remove the original temperature text column
weather_df.drop(
    columns=["temperature"],
    inplace=True
)

print("\nCleaned data:")
print(weather_df.head())

print("\nMissing values after cleaning:")
print(weather_df.isna().sum())

print("\nDuplicate rows after cleaning:")
print(weather_df.duplicated().sum())

print("\nCleaned DataFrame information:")
weather_df.info()
# Group the data by country
country_summary = (
    weather_df.groupby(
        "country",
        as_index=False
    )
    .agg(
        city_count=("city", "count"),
        average_temperature_c=("temperature_c", "mean"),
        minimum_temperature_c=("temperature_c", "min"),
        maximum_temperature_c=("temperature_c", "max")
    )
)

country_summary[
    [
        "average_temperature_c",
        "minimum_temperature_c",
        "maximum_temperature_c"
    ]
] = country_summary[
    [
        "average_temperature_c",
        "minimum_temperature_c",
        "maximum_temperature_c"
    ]
].round(1)

country_summary = country_summary.sort_values(
    "average_temperature_c",
    ascending=False
)

print("\nCountry temperature summary:")
print(country_summary.head(10))

# Filter for cities at or above 30 degrees Celsius
hot_cities = weather_df[
    weather_df["temperature_c"] >= 30
].copy()

hot_cities = hot_cities.sort_values(
    "temperature_c",
    ascending=False
)

print("\nCities at or above 30 degrees Celsius:")
print(
    hot_cities[
        [
            "city",
            "country",
            "condition",
            "temperature_c"
        ]
    ]
)

country_summary.to_csv(
    "country_temperature_summary.csv",
    index=False
)

hot_cities.to_csv(
    "hot_cities.csv",
    index=False
)
weather_df.to_csv(
    "clean_weather.csv",
    index=False
)

print("\nCleaned weather data saved to clean_weather.csv")