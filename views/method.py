"""Data & method: the SQL result tables, cleaning decisions, the test design and limits."""

import pandas as pd
import streamlit as st

from lib import data
from lib.site import NOTEBOOK_URL
from lib.ui import footer, header, md, section


def render() -> None:
    m = data.meta()
    s = m["raw_shapes"]

    header(
        "Data & method",
        "How the analysis was done",
        "The SQL results, the cleaning decisions, how the weather test was designed and the limits of the data. "
        f'The full Python work is in the <a href="{NOTEBOOK_URL}" target="_blank">notebook</a>.',
    )

    section("From SQL to Python")
    md("The project has two halves. First, SQL queries against a database of Chicago taxi trips and weather "
       "reports (based on the City of Chicago's public taxi trips data) produced three result tables. Second, those "
       "results were analysed in Python with pandas and SciPy.")
    st.table(pd.DataFrame([
        ("result_01", "Trips per taxi company in November 2017", f"{s['companies'][0]} companies"),
        ("result_04", "Average number of rides a day ending in each neighbourhood, November 2017",
         f"{s['dropoffs'][0]} neighbourhoods"),
        ("result_07", "Rides from the Loop to O'Hare on Saturdays: start time, weather (Good/Bad) and duration",
         f"{s['rides'][0]:,} rides on {len(m['saturdays'])} Saturdays"),
    ], columns=["SQL result", "What it holds", "Size"]), hide_index=True, border="horizontal")
    with st.expander("Look at the data"):
        t1, t2, t3 = st.tabs(["Companies", "Drop-offs", "Airport rides"])
        t1.dataframe(data.table("companies"), hide_index=True, height=300)
        t2.dataframe(data.table("dropoffs"), hide_index=True, height=300)
        t3.dataframe(data.table("rides")[["start_ts", "weather_conditions", "duration_seconds"]], hide_index=True,
                     height=300)

    section("Cleaning decisions")
    st.table(pd.DataFrame([
        ("Average drop-offs", "Stored with decimals (10727.47)", "Kept as averages, with decimals"),
        ("Identical ride rows", f"{m['duplicate_rides']} rows repeat another row exactly",
         f"Kept by default: start times are rounded to the hour ({m['distinct_start_times']} distinct start times "
         "for 1,068 rides), so identical rows are expected for different rides. A toggle shows the result without them"),
        ("0-second rides", f"{m['zero_duration']} rides", "Excluded from the test: impossible for an airport run"),
        ("Start time", "Text", "Converted to a timestamp; the start hour extracted"),
    ], columns=["Item", "What was found", "How it was handled"]), hide_index=True, border="horizontal")

    section("How the weather test was designed")
    md("- **Welch's t-test** compares the two average durations without assuming equal spread.\n"
       "- **Same-hour comparison.** Rainy rides are concentrated in the afternoon, which is slower anyway. A "
       "regression of duration on weather plus a separate term for each start hour compares rides that started "
       "at the same hour, so time of day can't masquerade as a weather effect.\n"
       "- Significance level 0.05 by default; adjustable on the test page.")

    section("Limits of this data")
    md("- **One month.** November 2017 only; no seasonality.\n"
       "- **Saturdays only** for the airport rides, and only four of them; weekday traffic may behave differently.\n"
       "- **Two weather labels.** \"Bad\" lumps together light rain and heavy storms.\n"
       "- **Hour, not minute.** Start times are rounded to the hour, so finer timing effects are invisible.")

    section("How this app is built")
    md("Python, pandas, SciPy and Plotly in a Streamlit app. `build_data.py` converts the three SQL result CSVs "
       f"into Parquet files that ship with the app. Data built on {m['built']}.")

    footer()
