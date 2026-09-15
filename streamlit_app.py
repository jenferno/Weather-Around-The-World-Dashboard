"""Explore scraped weather observations stored in weather_data.db."""

from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="World Weather Dashboard",
    page_icon="🌎",
    layout="wide",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* =========================
       MAIN BACKGROUND
       ========================= */

    .stApp {
        background-color: #303133;
        color: white;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #303133;
    }

    [data-testid="stHeader"] {
        background-color: transparent;
    }


    /* =========================
       SIDEBAR
       ========================= */

    [data-testid="stSidebar"] {
        background-color: #252628;
    }

    [data-testid="stSidebar"] h2 {
        color: white;
    }

    [data-testid="stSidebar"] label {
        color: #dddddd !important;
    }


    /* =========================
       PAGE TITLE
       ========================= */

    .dashboard-title {
        font-size: 42px;
        font-weight: 800;
        color: white;
        margin-bottom: 4px;
    }

    .dashboard-subtitle {
        color: #bdbdbd;
        font-size: 16px;
        margin-bottom: 25px;
    }


    /* =========================
       SECTION TITLES
       ========================= */

    .section-title {
        font-size: 28px;
        font-weight: 750;
        color: white;
        margin-top: 25px;
        margin-bottom: 4px;
    }

    .section-description {
        color: #bdbdbd;
        font-size: 14px;
        margin-bottom: 15px;
    }


    /* =========================
       WEATHER CARDS
       ========================= */

    .weather-card {
        background-color: #444547;
        border-radius: 22px;
        padding: 25px;
        min-height: 190px;
        border: 1px solid #555659;
        box-shadow: 7px 8px 0px #1f2021;
    }


    /* =========================
       METRIC CARDS
       ========================= */

    .metric-card {
        background-color: #444547;
        border-radius: 20px;
        padding: 20px;
        min-height: 125px;
        border: 1px solid #555659;
        box-shadow: 6px 7px 0px #1f2021;
    }

    .metric-icon {
        font-size: 28px;
        margin-bottom: 7px;
    }

    .metric-value {
        color: white;
        font-size: 27px;
        font-weight: 800;
    }

    .metric-label {
        color: #bdbdbd;
        font-size: 14px;
        margin-top: 4px;
    }


    /* =========================
       WEATHER ICON
       ========================= */

    .weather-icon {
        font-size: 55px;
        margin-bottom: 8px;
    }


    /* =========================
       WEATHER TEXT
       ========================= */

    .card-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .weather-condition {
        color: white;
        font-size: 28px;
        font-weight: 800;
    }

    .weather-description {
        color: #c7c7c7;
        font-size: 14px;
        margin-top: 5px;
    }

    .big-temperature {
        color: white;
        font-size: 55px;
        font-weight: 800;
        line-height: 1;
    }

    .temperature-description {
        color: #c7c7c7;
        font-size: 14px;
        margin-top: 6px;
    }

    .temperature-extreme {
        color: white;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 12px;
    }


    /* =========================
       STREAMLIT ELEMENTS
       ========================= */

    div[data-baseweb="select"] > div {
        background-color: #3c3d3f;
        border-radius: 12px;
        border: 1px solid #555659;
    }

    [data-testid="stExpander"] {
        background-color: #444547;
        border-radius: 18px;
        border: 1px solid #555659;
    }

    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# WEATHER ICON FUNCTION
# ============================================================

def get_weather_icon(condition):
    """Return an emoji based on the weather condition."""

    condition = str(condition).lower()

    if "thunder" in condition or "storm" in condition:
        return "⛈️"

    if "snow" in condition or "ice" in condition:
        return "❄️"

    if "rain" in condition or "drizzle" in condition:
        return "🌧️"

    if "fog" in condition or "mist" in condition:
        return "🌫️"

    if "partly" in condition:
        return "🌤️"

    if "cloud" in condition or "overcast" in condition:
        return "☁️"

    if "clear" in condition or "sunny" in condition:
        return "☀️"

    return "🌤️"


# ============================================================
# DATABASE
# ============================================================

database_path = Path(__file__).resolve().parent / "weather_data.db"

if not database_path.is_file():
    st.error(
        "Place weather_data.db beside streamlit_app.py before running the dashboard."
    )
    st.stop()


try:
    with sqlite3.connect(
        database_path.as_uri() + "?mode=ro",
        uri=True,
    ) as connection:

        df = pd.read_sql_query(
            "SELECT * FROM clean_weather",
            connection,
        )

except (sqlite3.Error, pd.errors.DatabaseError) as error:
    st.error(f"Unable to read clean_weather: {error}")
    st.stop()


# ============================================================
# DATA VALIDATION
# ============================================================

required_columns = {
    "city",
    "country",
    "condition",
    "temperature_c",
    "scraped_at",
}

if not required_columns.issubset(df.columns):
    st.error(
        "The clean_weather table is missing required weather columns."
    )
    st.stop()


df["temperature_c"] = pd.to_numeric(
    df["temperature_c"],
    errors="coerce",
)

df["scraped_at"] = pd.to_datetime(
    df["scraped_at"],
    errors="coerce",
    utc=True,
)

for column in ["city", "country", "condition"]:
    df[column] = (
        df[column]
        .fillna("Unknown")
        .astype(str)
    )


# ============================================================
# REMOVE INVALID TEMPERATURES
# ============================================================

missing_temperatures = df["temperature_c"].isna().sum()

df = df.dropna(
    subset=["temperature_c"]
).copy()


if missing_temperatures:
    st.caption(
        f"Excluded {missing_temperatures} observations with missing temperatures."
    )


if df.empty:
    st.warning(
        "No observations with valid temperatures are available."
    )
    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="dashboard-title">
        🌎 World Weather Dashboard
    </div>

    <div class="dashboard-subtitle">
        Explore temperatures and weather conditions from scraped city observations.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LATEST SCRAPE
# ============================================================

latest = df["scraped_at"].max()

if pd.notna(latest):
    st.caption(
        f"🕐 Latest scrape: {latest.strftime('%Y-%m-%d %H:%M UTC')}"
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <h2>🌤️ Explore Weather</h2>
    """,
    unsafe_allow_html=True,
)

st.sidebar.write(
    "Use the filters below to update the dashboard."
)


countries = st.sidebar.multiselect(
    "🌎 Countries",
    sorted(df["country"].unique()),
    default=sorted(df["country"].unique()),
)


conditions = st.sidebar.multiselect(
    "☁️ Weather Conditions",
    sorted(df["condition"].unique()),
    default=sorted(df["condition"].unique()),
)


unit = st.sidebar.selectbox(
    "🌡️ Temperature Unit",
    ["Celsius", "Fahrenheit"],
)


# ============================================================
# TEMPERATURE CONVERSION
# ============================================================

if unit == "Celsius":

    df["display_temperature"] = df["temperature_c"]

    unit_label = "°C"

else:

    df["display_temperature"] = (
        df["temperature_c"] * 9 / 5 + 32
    )

    unit_label = "°F"


temperature_column = "display_temperature"


# ============================================================
# TEMPERATURE SLIDER
# ============================================================

low = float(df[temperature_column].min())
high = float(df[temperature_column].max())


if low < high:

    temperature_range = st.sidebar.slider(
        f"🌡️ Temperature Range ({unit_label})",
        min_value=low,
        max_value=high,
        value=(low, high),
    )

else:

    temperature_range = (low, high)


# ============================================================
# FILTER DATA
# ============================================================

filtered = df[
    df["country"].isin(countries)
    & df["condition"].isin(conditions)
    & df[temperature_column].between(
        temperature_range[0],
        temperature_range[1],
    )
].copy()


if filtered.empty:

    st.warning(
        "No observations match these filters. "
        "Select more countries or conditions, "
        "or widen the temperature range."
    )

    st.stop()


# ============================================================
# CALCULATE METRICS
# ============================================================

average_temperature = filtered[
    temperature_column
].mean()

warmest_temperature = filtered[
    temperature_column
].max()

coolest_temperature = filtered[
    temperature_column
].min()

number_of_observations = len(filtered)

number_of_countries = filtered[
    "country"
].nunique()

most_common_condition = (
    filtered["condition"]
    .value_counts()
    .idxmax()
)

most_common_condition_count = (
    filtered["condition"]
    .value_counts()
    .max()
)

weather_icon = get_weather_icon(
    most_common_condition
)


# ============================================================
# METRIC CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-icon">📊</div>

            <div class="metric-value">
                {number_of_observations:,}
            </div>

            <div class="metric-label">
                Matching Observations
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-icon">🌎</div>

            <div class="metric-value">
                {number_of_countries}
            </div>

            <div class="metric-label">
                Countries
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-icon">🌡️</div>

            <div class="metric-value">
                {average_temperature:.1f} {unit_label}
            </div>

            <div class="metric-label">
                Average Temperature
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col4:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-icon">🔥</div>

            <div class="metric-value">
                {warmest_temperature:.1f} {unit_label}
            </div>

            <div class="metric-label">
                Warmest Observation
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# WEATHER OVERVIEW
# ============================================================

st.markdown(
    """
    <div class="section-title">
        ☀️ Weather Overview
    </div>

    <div class="section-description">
        A quick visual summary of the filtered weather observations.
    </div>
    """,
    unsafe_allow_html=True,
)


overview_col1, overview_col2 = st.columns([1, 2])


# ------------------------------------------------------------
# MOST COMMON CONDITION
# ------------------------------------------------------------

with overview_col1:

    st.markdown(
        f"""
        <div class="weather-card">

            <div class="weather-icon">
                {weather_icon}
            </div>

            <div class="card-title">
                Most Common Condition
            </div>

            <div class="weather-condition">
                {most_common_condition}
            </div>

            <div class="weather-description">
                Reported in {most_common_condition_count:,}
                observations
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# TEMPERATURE SUMMARY
# ------------------------------------------------------------

with overview_col2:

    st.markdown(
        f"""
        <div class="weather-card">

            <div class="card-title">
                🌡️ Temperature Summary
            </div>

            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 25px;
            ">

                <div>

                    <div class="big-temperature">
                        {average_temperature:.1f}{unit_label}
                    </div>

                    <div class="temperature-description">
                        Average temperature
                    </div>

                </div>

                <div style="text-align: right;">

                    <div class="temperature-extreme">
                        🔥 Warmest:
                        {warmest_temperature:.1f}{unit_label}
                    </div>

                    <div class="temperature-extreme">
                        🧊 Coolest:
                        {coolest_temperature:.1f}{unit_label}
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AVERAGE TEMPERATURE BY COUNTRY
# ============================================================

st.markdown(
    """
    <div class="section-title">
        🌎 Average Temperature by Country
    </div>

    <div class="section-description">
        Compare average temperatures among the observations
        matching your filters.
    </div>
    """,
    unsafe_allow_html=True,
)


summary = (
    filtered
    .groupby("country", as_index=False)[temperature_column]
    .mean()
    .sort_values(
        temperature_column,
        ascending=False,
    )
)


labels = {
    temperature_column: f"Temperature ({unit_label})",
    "country": "Country",
    "condition": "Weather Condition",
    "count": "Observations",
}


country_chart = px.bar(
    summary,
    x=temperature_column,
    y="country",
    orientation="h",
    labels=labels,
)


country_chart.update_layout(
    height=max(
        450,
        len(summary) * 30 + 150,
    ),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(
        color="white"
    ),
    yaxis=dict(
        autorange="reversed",
        automargin=True,
        title="",
    ),
    xaxis=dict(
        gridcolor="#555659",
        zerolinecolor="#555659",
    ),
    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20,
    ),
)


st.plotly_chart(
    country_chart,
    use_container_width=True,
)


# ============================================================
# TEMPERATURE DISTRIBUTION + CONDITIONS
# ============================================================

chart_col1, chart_col2 = st.columns(2)


# ------------------------------------------------------------
# TEMPERATURE DISTRIBUTION
# ------------------------------------------------------------

with chart_col1:

    st.markdown(
        """
        <div class="section-title">
            🌡️ Temperature Distribution
        </div>

        <div class="section-description">
            See how frequently different temperatures occur.
        </div>
        """,
        unsafe_allow_html=True,
    )

    histogram = px.histogram(
        filtered,
        x=temperature_column,
        nbins=20,
        labels=labels,
    )

    histogram.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="white"
        ),
        xaxis=dict(
            gridcolor="#555659",
            zerolinecolor="#555659",
        ),
        yaxis=dict(
            gridcolor="#555659",
            zerolinecolor="#555659",
            title="Observations",
        ),
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    st.plotly_chart(
        histogram,
        use_container_width=True,
    )


# ------------------------------------------------------------
# WEATHER CONDITIONS
# ------------------------------------------------------------

with chart_col2:

    st.markdown(
        """
        <div class="section-title">
            ☁️ Weather Conditions
        </div>

        <div class="section-description">
            Compare the number of observations for each condition.
        </div>
        """,
        unsafe_allow_html=True,
    )

    counts = (
        filtered
        .groupby("condition")
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False,
        )
    )


    condition_chart = px.bar(
        counts,
        x="count",
        y="condition",
        orientation="h",
        labels=labels,
    )


    condition_chart.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="white"
        ),
        xaxis=dict(
            gridcolor="#555659",
            zerolinecolor="#555659",
        ),
        yaxis=dict(
            automargin=True,
            autorange="reversed",
            title="",
        ),
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )


    st.plotly_chart(
        condition_chart,
        use_container_width=True,
    )


# ============================================================
# FILTERED DATA
# ============================================================

with st.expander("📋 View Filtered Observations"):

    display = filtered[
        [
            "city",
            "country",
            "condition",
            temperature_column,
            "scraped_at",
        ]
    ].rename(
        columns={
            temperature_column:
                f"Temperature ({unit_label})"
        }
    )


    st.dataframe(
        display,
        hide_index=True,
        use_container_width=True,
    )


    st.download_button(
        "⬇️ Download Filtered Observations",
        display.to_csv(index=False),
        "filtered_weather.csv",
        "text/csv",
    )