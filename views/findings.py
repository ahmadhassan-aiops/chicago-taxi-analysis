"""Landing page: the questions from the ride-sharing company, the findings and recommendations."""

import plotly.graph_objects as go
import streamlit as st

from lib import charts, data
from lib.ui import cap, finding, footer, header, method_card, recommendations, spotlight


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
        chips=[("database", "SQL"), ("code", "Python, pandas"), ("functions", "SciPy hypothesis test"),
               ("calendar_month", "November 2017")],
    )

    k = st.columns(4)
    k[0].metric("Taxi companies", m["companies"], border=True)
    k[1].metric("Trips by these companies", f"{m['trips_total']:,}", border=True)
    k[2].metric("Drop-off neighbourhoods", m["neighborhoods"], border=True)
    k[3].metric("Loop to O'Hare rides studied", f"{len(r):,}", border=True)

    top = d.head(10)
    colours = [charts.BLUE if i < 4 else charts.ORANGE if n == "O'Hare" else charts.QUIET
               for i, n in enumerate(top["dropoff_location_name"])]
    fig = go.Figure(go.Bar(
        x=top["average_trips"], y=top["dropoff_location_name"], orientation="h",
        marker=dict(color=colours, line=dict(width=0), cornerradius=4),
        text=[f"{v:,.0f}" for v in top["average_trips"]], textposition="outside",
        textfont=dict(color=charts.INK_2, size=12), cliponaxis=False,
        customdata=(top["average_trips"] / d["average_trips"].sum()).values,
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} rides a day (%{customdata:.1%} of all drop-offs)<extra></extra>",
    ))
    charts.style(fig, height=380)
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=charts.INK_2))
    fig.update_xaxes(showgrid=True, gridcolor=charts.GRID, title="Average drop-offs per day")
    spotlight("Where Chicago's taxi rides end",
              f"Average rides a day into the ten busiest neighbourhoods. The <b>four downtown areas</b> (amber) take "
              f"{d4:.0%} of all drop-offs across {len(d)} neighbourhoods; <b>O'Hare</b> (slate) is the one big "
              "destination outside the centre, and the premium route this analysis follows.", fig, key="spot")

    st.subheader("Key findings", anchor=False)
    a = st.columns(3)
    finding(a[0], f"{top10:.0%}", f"of trips go to the top 10 of {m['companies']} companies",
            "Ten companies run most trips",
            f"{c.iloc[0]['company_name']} alone ran {c.iloc[0]['trips_amount']:,} trips, "
            f"{c.iloc[0]['trips_amount'] / c['trips_amount'].sum():.0%} of the total. Half of the companies ran "
            f"fewer than {c['trips_amount'].median():.0f}.", COMPANIES, "Taxi companies", card_icon="local_taxi")
    finding(a[1], f"{d4:.0%}", "of drop-offs end in four central neighbourhoods",
            "Rides end downtown",
            f"{', '.join(d['dropoff_location_name'].head(4))} take the lion's share; O'Hare airport is fifth. "
            "Demand is concentrated in a small area.", DROPOFFS, "Drop-off neighbourhoods", card_icon="pin_drop")
    finding(a[2], f"+{adj['effect']:.1f} min", "longer Loop to O'Hare ride in rain, at the same hour",
            "Rain slows the airport run",
            f"Raw averages differ by {raw['Bad'] - raw['Good']:.1f} min, but rainy rides happen more in the slow "
            f"afternoon. Compared at the same hour, rain still adds about {adj['effect']:.0f} min (p &lt; 0.001).",
            WEATHER, "Rain and the airport run", card_icon="rainy")

    st.subheader("What I would recommend", anchor=False)
    recommendations([
        ("location_city", "Launch downtown first",
         "The Loop, River North, Streeterville and West Loop are where most rides end: that is where cars should wait."),
        ("flight_takeoff", "Treat O'Hare as a premium route",
         "It is the busiest destination outside the centre, and its rides are long."),
        ("umbrella", "Price and plan for rain",
         f"Expect about <b>{adj['effect']:.0f} extra minutes</b> on airport runs in bad weather; quote longer arrival "
         "times and consider weather-based pricing."),
        ("leaderboard", "Benchmark against the leaders",
         "Flash Cab and the next few companies set the service level passengers compare against, but no single "
         "company dominates, so a newcomer can win share."),
    ])
    cap("November 2017 only, Saturdays only for the airport rides: a starting point for a launch plan, not a "
        "forecast.")
    method_card("<b>How this was done.</b> SQL queries on the Chicago taxi database produced three result tables; "
                "Python cleaned them, ranked companies and neighbourhoods and tested the weather hypothesis, "
                "first straight and then at the same hour of day.", METHOD,
                tools=["SQL", "pandas", "SciPy", "Welch's t-test", "Regression"])

    footer()
