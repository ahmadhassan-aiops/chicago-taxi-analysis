"""Rain and the airport run: does bad weather change Loop to O'Hare ride durations on Saturdays? (notebook test)"""

import pandas as pd
import streamlit as st
from scipy import stats

from lib import charts, data
from lib.ui import chart, footer, header, insight, md, note, section


def render() -> None:
    m = data.meta()

    header(
        "Hypothesis test",
        "Rain and the airport run",
        "Rides from the Loop to O'Hare on the four Saturdays of November 2017, with the weather at the start of "
        "each ride. Does rain change how long the ride takes?",
    )

    a, b, c = st.columns(3)
    alpha = a.select_slider("Significance level (α)", options=[0.01, 0.05, 0.10], value=0.05, key="alpha")
    dedup = b.toggle("Remove identical rows", value=False, key="dedup",
                     help=f"{m['duplicate_rides']} rows repeat another row exactly. Start times are rounded to the "
                          "hour, so these are most likely different rides with the same hour and duration.")
    drop0 = c.toggle("Remove 0-second rides", value=True, key="drop0",
                     help=f"{m['zero_duration']} rides last 0 seconds: recording errors.")
    r = data.rides(drop_duplicates=dedup, drop_zero=drop0)
    good, bad = r.loc[r.weather_conditions == "Good", "minutes"], r.loc[r.weather_conditions == "Bad", "minutes"]

    md("- **H₀ (null):** the average duration of Loop to O'Hare rides is the same on rainy and on dry Saturdays.\n"
       "- **H₁ (alternative):** the average duration differs.")

    section("1. Straight comparison", "Welch's t-test on all rides.")
    t = stats.ttest_ind(bad, good, equal_var=False)
    k = st.columns(4)
    k[0].metric("Dry, average", f"{good.mean():.1f} min", border=True)
    k[1].metric("Rain, average", f"{bad.mean():.1f} min", border=True)
    k[2].metric("Difference", f"+{bad.mean() - good.mean():.1f} min", border=True)
    k[3].metric("p-value", f"{t.pvalue:.2g}", border=True)
    chart(charts.histograms({"Dry (Good)": good, "Rain (Bad)": bad}, bin_size=5, start=0,
                            xtitle="Ride duration (minutes)", unit=" min"))
    insight(f"{'<b>Reject H₀.</b>' if t.pvalue < alpha else '<b>Do not reject H₀.</b>'} Rainy rides average "
            f"{bad.mean() - good.mean():.1f} minutes longer ({len(bad)} rainy, {len(good)} dry rides, p = {t.pvalue:.2g}).")

    section("2. Is it the rain, or the time of day?", "When the rainy rides started.")
    hourly = r.groupby(["hour", "weather_conditions"]).size().unstack(fill_value=0).reindex(range(24), fill_value=0)
    share = hourly.div(hourly.sum())
    chart(charts.grouped_bars([f"{h}:00" for h in share.index],
                              {"Dry (Good)": share.get("Good", pd.Series(0, index=share.index)).values,
                               "Rain (Bad)": share.get("Bad", pd.Series(0, index=share.index)).values},
                              hover_fmt=".0%", ytitle="Share of the group's rides").update_yaxes(tickformat=".0%"))
    by_hour = r.groupby("hour")["minutes"].mean()
    aft = r.groupby("weather_conditions")["hour"].apply(lambda h: h.between(12, 17).mean())
    insight(f"<b>{aft['Bad']:.0%}</b> of rainy rides started between noon and 6 pm, against {aft['Good']:.0%} of dry "
            f"rides, and that is when the drive is slowest anyway (rides starting 12-5 pm average "
            f"{by_hour.loc[12:17].mean():.0f} min against {by_hour.loc[5:9].mean():.0f} min at 5-9 am). Part of the "
            "straight comparison is therefore the afternoon traffic, not the rain.")

    section("3. Compared at the same hour", "Regression: duration on weather plus one term per start hour.")
    adj = data.weather_effect_same_hour(r)
    k = st.columns(3)
    k[0].metric("Effect of rain, same hour", f"+{adj['effect']:.1f} min", border=True)
    k[1].metric("95% confidence interval", f"{adj['lo']:.1f} to {adj['hi']:.1f} min", border=True)
    k[2].metric("p-value", f"{adj['p']:.2g}", border=True)
    raw = bad.mean() - good.mean()
    insight(f"{'<b>Reject H₀ again.</b>' if adj['p'] < alpha else '<b>Do not reject H₀.</b>'} Comparing rides "
            f"that started at the same hour, rain adds about <b>{adj['effect']:.1f} minutes</b>, smaller than the "
            f"raw {raw:.1f} but clearly real. About {1 - adj['effect'] / raw:.0%} of the raw gap was the time of day.")

    note("The original notebook ran only the straight comparison, and removed the identical rows as duplicates. "
         "Start times are rounded to the hour, so identical rows are most likely separate rides; the toggle above "
         "shows the conclusion holds either way.")

    footer()
