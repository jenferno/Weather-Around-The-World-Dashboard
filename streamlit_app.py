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
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #2f3032;
        color: #ffffff;
    }

    .main {
        background: #2f3032;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stAppViewContainer"] {
        background: #2f3032;
    }

    /* ---------- SIDEBAR ---------- */

    [data-testid="stSidebar"] {
        background: #252628;
        border-right: 1px solid #444548;
    }

    [data-testid="stSidebar"] h2 {
        color: #ffffff;
        font-weight: 700;
    }

    [data-testid="stSidebar"] label {
        color: #dddddd !important;
        font-weight: 500;
    }

    /* ---------- MAIN TITLE ---------- */

    .dashboard-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 4px;
        color: #ffffff;
    }

    .dashboard-subtitle {
        color: #bcbcbc;
        font-size: 16px;
        margin-bottom: 28px;
    }

    /* ---------- CARDS ---------- */

    .weather-card {
        background: #444547;
        border-radius: 24px;
        padding: 28px;
        box-shadow: 8px 10px 0px #1e1f20;
        border: 1px solid #4f5052;
    }

    .small-card {
        background: #444547;
        border-radius: 20px;
        padding: 22px;
        box-shadow: 6px 7px 0px #1e1f20;
        border: 1px solid #4f5052;
        min-height: 135px;
    }

    /* ---------- ICONS ---------- */

    .weather-icon {
        font-size: 58px;
        line-height: 1;
        margin-bottom: 8px;
    }

    .metric-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }

    /* ---------- TEMPERATURE ---------- */

    .temperature {
        font-size: 64px;
        font-weight: 800;
        line-height: 1;
        color: #ffffff;
    }

    .temperature-label {
        color: #bbbbbb;
        font-size: 15px;
        margin-top: 5px;
    }

    /* ---------- CARD TEXT ---------- */

    .card-title {
        color: #ffffff;
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .card-subtitle {
        color: #bdbdbd;
        font-size: 14px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
    }

    .metric-label {
        color: #bcbcbc;
        font-size: 14px;
        margin-top: 3px;
    }

    /* ---------- SECTION HEADERS ---------- */

    .section-title {
        font-size: 28px;
        font-weight: 750;
        color: #ffffff;
        margin-top: 30px;
        margin-bottom: 5px;
    }

    .section-description {
        color: #bcbcbc;
        margin-bottom: 15px;
    }

    /* ---------- FILTER BUTTONS ---------- */

    .stButton > button {
        border-radius: 14px;
        border: none;
        background: #4bc51b;
        color: white;
        font-weight: 700;
    }

    /* ---------- MULTISELECT ---------- */

    div[data-baseweb="select"] > div {
        background-color: #3c3d3f;
        border-radius: 12px;
        border: 1px solid #555659;
    }

    /* ---------- SLIDER ---------- */

    div[data-testid="stSlider"] {
        padding-top: 8px;
    }

    /* ---------- EXPANDER ---------- */

    details {
        background: #444547 !important;
        border-radius: 18px !important;
        border: 1px solid #555659 !important;
    }

    details summary {
        color: white !important;
        font-weight: 700 !important;
    }

    /* ---------- DATAFRAME ---------- */

    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_weather_icon(condition):
    """Return a weather icon based on the condition text."""

    condition = str(condition).lower()

    if "thunder" in condition or "storm" in condition:
        return "⛈️"

    if "snow" in condition or "ice" in condition:
        return "❄️"

    if "rain" in condition or "drizzle" in condition:
        return "🌧️"

    if "cloud" in condition or "overcast" in condition:
        return "☁️"

    if "partly" in condition:
        return "🌤️"

    if "clear" in condition or "sunny" in condition:
        return "☀️"

    if "fog" in condition or "mist" in condition:
        return "🌫️"

    return "🌤️"


# ============================================================
# LOAD DATABASE
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
# VALIDATE DATA
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


latest = df["scraped_at"].max()

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
    '<div class="dashboard-title">🌎 World Weather Dashboard</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="dashboard-subtitle">
        Explore scraped weather observations from cities around the world.
        Use the filters to interact with the dashboard.
    </div>
    """,
    unsafe_allow_html=True,
)


if pd.notna(latest):
    st.caption(
        f"🕐 Latest scrape: {latest.strftime('%Y-%m-%d %H:%M UTC')}"
    )


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.markdown(
    """
    <h2>🌤️ Explore Weather</h2>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    "Use the filters below to customize the dashboard."
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

temperature_column = "display_temperature"

if unit == "Celsius":
    df[temperature_column] = df["temperature_c"]
    unit_label = "°C"
else:
    df[temperature_column] = (
        df["temperature_c"] * 9 / 5 + 32
    )
    unit_label = "°F"


low = float(df[temperature_column].min())
high = float(df[temperature_column].max())


if low < high:

    temperature_range = st.sidebar.slider(
        f"🌡️ Temperature Range ({unit_label})",
        low,
        high,
        (low, high),
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
        *temperature_range
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
# TOP METRIC CARDS
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


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="small-card">
            <div class="metric-icon">📊</div>
            <div class="metric-value">{len(filtered):,}</div>
            <div class="metric-label">Matching Observations</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown(
        f"""
        <div class="small-card">
            <div class="metric-icon">🌎</div>
            <div class="metric-value">{filtered["country"].nunique()}</div>
            <div class="metric-label">Countries</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        f"""
        <div class="small-card">
            <div class="metric-icon">🌡️</div>
            <div class="metric-value">{average_temperature:.1f} {unit_label}</div>
            <div class="metric-label">Average Temperature</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col4:

    st.markdown(
        f"""
        <div class="small-card">
            <div class="metric-icon">🔥</div>
            <div class="metric-value">{warmest_temperature:.1f} {unit_label}</div>
            <div class="metric-label">Warmest Observation</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CURRENT WEATHER OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">🌤️ Weather Overview</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'A quick visual summary of the filtered weather observations.'
    '</div>',
    unsafe_allow_html=True,
)


# Find most common condition
common_condition = (
    filtered["condition"]
    .value_counts()
    .idxmax()
)

condition_count = (
    filtered["condition"]
    .value_counts()
    .max()
)

condition_icon = get_weather_icon(common_condition)


overview_col1, overview_col2 = st.columns([1, 2])


with overview_col1:

    st.markdown(
        f"""
        <div class="weather-card">

            <div class="weather-icon">
                {condition_icon}
            </div>

            <div class="card-title">
                Most Common Condition
            </div>

            <div class="temperature">
                {common_condition}
            </div>

            <div class="temperature-label">
                Reported in {condition_count:,} observations
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with overview_col2:

    st.markdown(
        f"""
        <div class="weather-card">

            <div class="card-title">
                🌡️ Temperature Summary
            </div>

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                margin-top:25px;
            ">

                <div>
                    <div class="temperature">
                        {average_temperature:.1f}{unit_label}
                    </div>

                    <div class="temperature-label">
                        Average temperature
                    </div>
                </div>

                <div style="text-align:right;">

                    <div style="
                        color:#ffffff;
                        font-size:18px;
                        font-weight:700;
                    ">
                        🔥 {warmest_temperature:.1f}{unit_label}
                    </div>

                    <div style="
                        color:#ffffff;
                        font-size:18px;
                        font-weight:700;
                        margin-top:10px;
                    ">
                        🧊 {coolest_temperature:.1f}{unit_label}
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# COUNTRY TEMPERATURE CHART
# ============================================================

st.markdown(
    '<div class="section-title">🌎 Average Temperature by Country</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-description">'
    'Compare average temperatures among the observations matching your filters.'
    '</div>',
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
    title="",
)


country_chart.update_layout(
    height=max(
        450,
        len(summary) * 30 + 150,
    ),
    yaxis={
        "autorange": "reversed",
        "automargin": True,
    },
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={
        "color": "white",
    },
    xaxis={
        "gridcolor": "#555659",
        "zerolinecolor": "#555659",
    },
    yaxis_title="",
    margin=dict(
        l=20,
        r=20,
        t=30,
        b=20,
    ),
)


st.plotly_chart(
    country_chart,
    use_container_width=True,
)


# ============================================================
# TWO-CHART SECTION
# ============================================================

chart_col1, chart_col2 = st.columns(2)


# ------------------------------------------------------------
# TEMPERATURE DISTRIBUTION
# ------------------------------------------------------------

with chart_col1:

    st.markdown(
        '<div class="section-title">🌡️ Temperature Distribution</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'How frequently different temperatures occur.'
        '</div>',
        unsafe_allow_html=True,
    )

    histogram = px.histogram(
        filtered,
        x=temperature_column,
        nbins=20,
        labels=labels,
        title="",
    )

    histogram.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        xaxis={
            "gridcolor": "#555659",
            "zerolinecolor": "#555659",
        },
        yaxis={
            "gridcolor": "#555659",
            "zerolinecolor": "#555659",
            "title": "Observations",
        },
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
        '<div class="section-title">☁️ Weather Conditions</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-description">'
        'Compare the number of observations for each condition.'
        '</div>',
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
        title="",
    )

    condition_chart.update_layout(
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"},
        xaxis={
            "gridcolor": "#555659",
            "zerolinecolor": "#555659",
        },
        yaxis={
            "automargin": True,
            "autorange": "reversed",
            "title": "",
        },
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