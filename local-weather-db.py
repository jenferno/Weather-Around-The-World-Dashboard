from pathlib import Path
import sqlite3

import pandas as pd


# Locate files relative to this Python script.
project_folder = Path(__file__).resolve().parent
database_path = project_folder / "weather_data.db"

csv_tables = {
    "raw_weather.csv": "raw_weather",
    "clean_weather.csv": "clean_weather",
    "country_temperature_summary.csv": "country_temperature_summary",
    "hot_cities.csv": "hot_cities"
}

try:
    with sqlite3.connect(database_path) as conn:
        for csv_filename, table_name in csv_tables.items():
            csv_path = project_folder / csv_filename
            dataframe = pd.read_csv(csv_path)

            dataframe.to_sql(
                table_name,
                conn,
                if_exists="replace",
                index=False
            )

            print(
                f"Loaded {len(dataframe)} rows "
                f"from {csv_filename} into {table_name}."
            )

        print("\nVerifying database tables:")

        for table_name in csv_tables.values():
            query = f"SELECT COUNT(*) AS row_count FROM {table_name}"
            result = pd.read_sql_query(query, conn)
            row_count = result.loc[0, "row_count"]

            print(f"{table_name}: {row_count} rows")

    print(f"\nDatabase saved as {database_path.name}.")

except (FileNotFoundError, sqlite3.Error, pd.errors.DatabaseError) as error:
    print(f"Database loading error: {error}")