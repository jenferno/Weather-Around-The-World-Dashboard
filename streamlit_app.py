"""Explore scraped weather observations stored in weather_data.db."""

from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="World Weather Dashboard", layout="wide")
st.title("World Weather Dashboard")
st.write("Explore temperatures and weather conditions in the scraped city observations. Use the sidebar filters to update all three charts.")
st.caption("This dashboard shows saved observations, not a live weather feed. Country averages describe the sampled observations only.")

database_path = Path(__file__).resolve().parent / "weather_data.db"
if not database_path.is_file():
    st.error("Place weather_data.db beside streamlit_app.py before running the dashboard.")
    st.stop()

try:
    with sqlite3.connect(database_path.as_uri() + "?mode=ro", uri=True) as connection:
        df = pd.read_sql_query("SELECT * FROM clean_weather", connection)
except (sqlite3.Error, pd.errors.DatabaseError) as error:
    st.error(f"Unable to read clean_weather: {error}")
    st.stop()

required_columns = {"city", "country", "condition", "temperature_c", "scraped_at"}
if not required_columns.issubset(df.columns):
    st.error("The clean_weather table is missing required weather columns.")
    st.stop()

df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="coerce")
df["scraped_at"] = pd.to_datetime(df["scraped_at"], errors="coerce", utc=True)
latest = df["scraped_at"].max()
if pd.notna(latest):
    st.caption(f"Latest scrape in database: {latest.strftime('%Y-%m-%d %H:%M UTC')}")
for column in ["city", "country", "condition"]:
    df[column] = df[column].fillna("Unknown").astype(str)
missing_temperatures = df["temperature_c"].isna().sum()
df = df.dropna(subset=["temperature_c"]).copy()
if missing_temperatures:
    st.caption(f"Excluded {missing_temperatures} observations with missing temperatures.")
if df.empty:
    st.warning("No observations with valid temperatures are available.")
    st.stop()

st.sidebar.header("Explore weather")
countries = st.sidebar.multiselect("Countries", sorted(df["country"].unique()), default=sorted(df["country"].unique()))
conditions = st.sidebar.multiselect("Weather conditions", sorted(df["condition"].unique()), default=sorted(df["condition"].unique()))
unit = st.sidebar.selectbox("Temperature unit", ["Celsius", "Fahrenheit"])
temperature_column = "display_temperature"
df[temperature_column] = df["temperature_c"] if unit == "Celsius" else df["temperature_c"] * 9 / 5 + 32
unit_label = "°C" if unit == "Celsius" else "°F"
low, high = float(df[temperature_column].min()), float(df[temperature_column].max())
if low < high:
    temperature_range = st.sidebar.slider(f"Temperature range ({unit_label})", low, high, (low, high))
else:
    temperature_range = (low, high)
filtered = df[
    df["country"].isin(countries)
    & df["condition"].isin(conditions)
    & df[temperature_column].between(*temperature_range)
].copy()
if filtered.empty:
    st.warning("No observations match these filters. Select more countries or conditions, or widen the temperature range.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric("Matching observations", len(filtered))
col2.metric("Countries", filtered["country"].nunique())
col3.metric("Average temperature", f"{filtered[temperature_column].mean():.1f} {unit_label}")
labels = {temperature_column: f"Temperature ({unit_label})", "country": "Country", "condition": "Weather Condition", "count": "Observations"}

st.subheader("Average temperature by country")
st.write("Compare average temperatures among the observations matching your filters.")
summary = filtered.groupby("country", as_index=False)[temperature_column].mean().sort_values(temperature_column, ascending=False)
country_chart = px.bar(
    summary,
    x=temperature_column,
    y="country",
    orientation="h",
    labels=labels,
    title="Average Temperature of Sampled Observations",
    color_discrete_sequence=["steelblue"],
)
country_chart.update_layout(
    height=max(450, len(summary) * 24 + 150),
    yaxis={"autorange": "reversed", "automargin": True},
)
st.plotly_chart(country_chart, use_container_width=True)

st.subheader("Temperature distribution")
st.write("See how frequently different temperatures occur in the filtered observations.")
histogram = px.histogram(filtered, x=temperature_column, nbins=20, labels=labels, title="Distribution of Observed Temperatures", color_discrete_sequence=["teal"])
histogram.update_layout(yaxis_title="Observations")
st.plotly_chart(histogram, use_container_width=True)

st.subheader("Weather conditions")
st.write("Compare the number of filtered observations reporting each weather condition.")
counts = filtered.groupby("condition").size().reset_index(name="count").sort_values("count", ascending=False)
condition_chart = px.bar(
    counts,
    x="count",
    y="condition",
    orientation="h",
    labels=labels,
    title="Observations by Weather Condition",
    color_discrete_sequence=["darkorange"],
)
condition_chart.update_layout(
    height=max(450, len(counts) * 28 + 150),
    yaxis={"autorange": "reversed", "automargin": True},
)
st.plotly_chart(condition_chart, use_container_width=True)

with st.expander("View the filtered observations"):
    display = filtered[["city", "country", "condition", temperature_column, "scraped_at"]].rename(columns={temperature_column: f"Temperature ({unit_label})"})
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.download_button("Download filtered observations", display.to_csv(index=False), "filtered_weather.csv", "text/csv")