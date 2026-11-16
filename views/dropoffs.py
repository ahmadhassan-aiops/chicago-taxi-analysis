"""Drop-off neighbourhoods: where rides end (notebook part 1)."""

import streamlit as st

from lib import charts, data
from lib.ui import chart, footer, header, insight, section


def render() -> None:
    d = data.table("dropoffs")
    total = d["average_trips"].sum()

    header("Demand", "Drop-off neighbourhoods",
           f"Average daily number of rides ending in each of {len(d)} Chicago neighbourhoods in November 2017.")

    section("Top neighbourhoods", "Q1. The neighbourhoods with the most drop-offs.")
    k = st.slider("Neighbourhoods to show", 5, 30, 10, key="k")
    top = d.head(k)
    chart(charts.bars(top["dropoff_location_name"].values, top["average_trips"].values, horizontal=True,
                      highlight=(top["dropoff_location_name"] == "O'Hare").values == False,  # noqa: E712
                      customdata=(top["average_trips"] / total).values[:, None],
                      hover="<b>%{y}</b><br>%{x:,.0f} rides a day (%{customdata[0]:.1%})",
                      xtitle="Average drop-offs per day"))
    insight(f"The Loop ({d.iloc[0]['average_trips']:,.0f} a day) and River North ({d.iloc[1]['average_trips']:,.0f}) "
            f"lead, then Streeterville and West Loop: all central. <b>O'Hare</b> (grey) is the only top-5 "
            "destination outside the centre: the airport run.")

    section("A long tail", "How many neighbourhoods account for most drop-offs.")
    cum = d["average_trips"].cumsum() / total
    n80 = int((cum < 0.8).sum()) + 1
    chart(charts.bars(d["dropoff_location_name"].values, d["average_trips"].values,
                      highlight=(d.index < n80).tolist(),
                      hover="<b>%{x}</b><br>%{y:,.1f} rides a day", ytitle="Average drop-offs per day")
          .update_xaxes(showticklabels=False, title=f"All {len(d)} neighbourhoods, ranked"))
    insight(f"<b>{n80} of {len(d)}</b> neighbourhoods (highlighted) receive 80% of drop-offs. The median "
            f"neighbourhood gets about {d['average_trips'].median():.0f} rides a day, against "
            f"{d.iloc[0]['average_trips']:,.0f} in the Loop.")

    footer()
