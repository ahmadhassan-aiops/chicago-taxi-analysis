"""Taxi companies: trips per company and how concentrated the market is (notebook part 2)."""

import numpy as np
import streamlit as st

from lib import charts, data
from lib.ui import chart, footer, header, insight, section


def render() -> None:
    c = data.table("companies")
    total = c["trips_amount"].sum()

    header("Competitors", "Taxi companies",
           f"{len(c)} taxi companies ran {total:,} trips in November 2017. How the market is split tells a new "
           "entrant who it is really up against.")

    section("Top companies by trips", "Q2. Number of trips per company.")
    k = st.slider("Companies to show", 5, 30, 10, key="k")
    top = c.head(k)
    chart(charts.bars(top["company_name"].values, top["trips_amount"].values, horizontal=True,
                      customdata=(top["trips_amount"] / total).values[:, None],
                      hover="<b>%{y}</b><br>%{x:,} trips (%{customdata[0]:.1%} of all)", xtitle="Trips"))
    insight(f"<b>{c.iloc[0]['company_name']}</b> leads with {c.iloc[0]['trips_amount']:,} trips, followed by "
            f"{c.iloc[1]['company_name']} ({c.iloc[1]['trips_amount']:,}). Below the top group, trip counts fall "
            "off quickly.")

    section("How concentrated is the market?", "Cumulative share of trips, companies ranked from biggest to smallest.")
    cum = c["trips_amount"].cumsum() / total
    rank = np.arange(1, len(c) + 1)
    fig = charts.lines(rank, {"Cumulative share of trips": cum.round(4)}, hover_fmt=".1%", markers=False,
                       xtitle="Number of companies (largest first)", ytitle="Share of all trips")
    fig.update_yaxes(tickformat=".0%", range=[0, 1.02])
    chart(fig)
    n50 = int((cum < 0.5).sum()) + 1
    n90 = int((cum < 0.9).sum()) + 1
    shares = c["trips_amount"] / total
    hhi = float((shares * 100) ** 2 @ np.ones(len(shares)))
    insight(f"Just <b>{n50} companies</b> run half of all trips and {n90} run 90%. The remaining "
            f"{len(c) - n90} companies share the last 10%. Yet no company dominates: the concentration index (HHI) is {hhi:,.0f} on a 0-10,000 "
            "scale, below the 1,000 that competition authorities treat as concentrated. There is room for a new entrant.")

    section("All companies")
    st.dataframe(c.assign(share=shares).rename(columns={"company_name": "Company", "trips_amount": "Trips",
                                                        "share": "Share of trips"}),
                 hide_index=True, height=360,
                 column_config={"Trips": st.column_config.NumberColumn(format="localized"),
                                "Share of trips": st.column_config.ProgressColumn(format="percent", min_value=0,
                                                                                  max_value=float(shares.max()))})

    footer()
