"""Landing page: the questions from the ride-sharing company, the findings and recommendations."""

import streamlit as st

from lib import data
from lib.ui import cap, finding, footer, header, md


def render() -> None:
    from nav import COMPANIES, DROPOFFS, METHOD, WEATHER

    m = data.meta()
    c = data.table("companies")
    d = data.table("dropoffs")
    r = data.rides()
    raw = r.groupby("weather_conditions")["minutes"].mean()
    adj = data.weather_effect_same_hour(r)
    top10 = c["trips_amount"].head(10).sum() / c["trips_amount"].sum()
    d4 = d["average_trips"].head(4).sum() / d["average_trips"].sum()

    header(
        "SQL + Python data analysis",
        "Chicago taxis: who wins the market, where rides end, and does rain slow the airport run?",
        "A new ride-sharing company is launching in Chicago. With SQL I pulled taxi trip summaries for November "
        "2017 and weather records, then analysed them in Python to learn who the competitors are, where passengers "
        "go, and whether rain changes the duration of the busiest premium route, the Loop to O'Hare airport.",
    )

    k = st.columns(4)
    k[0].metric("Taxi companies", m["companies"], border=True)
    k[1].metric("Trips by these companies", f"{m['trips_total']:,}", border=True)
    k[2].metric("Drop-off neighbourhoods", m["neighborhoods"], border=True)
    k[3].metric("Loop to O'Hare rides studied", f"{len(r):,}", border=True)

    st.subheader("Key findings", anchor=False)
    a = st.columns(3)
    finding(a[0], f"{top10:.0%}", f"of trips go to the top 10 of {m['companies']} companies",
            "Ten companies run most trips",
            f"{c.iloc[0]['company_name']} alone ran {c.iloc[0]['trips_amount']:,} trips, "
            f"{c.iloc[0]['trips_amount'] / c['trips_amount'].sum():.0%} of the total. Half of the companies ran "
            f"fewer than {c['trips_amount'].median():.0f}.", COMPANIES, "Taxi companies")
    finding(a[1], f"{d4:.0%}", "of drop-offs end in four central neighbourhoods",
            "Rides end downtown",
            f"{', '.join(d['dropoff_location_name'].head(4))} take the lion's share; O'Hare airport is fifth. "
            "Demand is concentrated in a small area.", DROPOFFS, "Drop-off neighbourhoods")
    finding(a[2], f"+{adj['effect']:.1f} min", "longer Loop to O'Hare ride in rain, at the same hour",
            "Rain slows the airport run",
            f"Raw averages differ by {raw['Bad'] - raw['Good']:.1f} min, but rainy rides happen more in the slow "
            f"afternoon. Compared at the same hour, rain still adds about {adj['effect']:.0f} min (p &lt; 0.001).",
            WEATHER, "Rain and the airport run")

    st.subheader("What I would recommend", anchor=False)
    md("1. **Launch downtown first.** The Loop, River North, Streeterville and West Loop are where most rides end; "
       "that is where cars should wait.\n"
       "2. **Treat O'Hare as a premium route.** It is the busiest destination outside the centre, and its rides "
       "are long.\n"
       f"3. **Price and plan for rain.** Expect about {adj['effect']:.0f} extra minutes on airport runs in bad "
       "weather; quote longer arrival times and consider weather-based pricing.\n"
       "4. **Benchmark against the leaders, not the long tail.** Flash Cab and the next few companies set the "
       "service level passengers compare against, but no single company dominates, so a newcomer can win share.")
    cap("November 2017 only, Saturdays only for the airport rides: a starting point for a launch plan, not a "
        "forecast.")
    with st.container(border=True):
        md("**How this was done.** SQL queries on the Chicago taxi database produced three result tables; Python "
           "(pandas, SciPy) cleaned them, ranked companies and neighbourhoods and tested the weather hypothesis.")
        st.page_link(METHOD, label="Data & method", icon=":material/arrow_forward:")

    footer()
