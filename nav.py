"""Page registry, shared by app.py and pages that link to other pages."""

import streamlit as st

from views import companies, dropoffs, findings, method, weather

FINDINGS = st.Page(findings.render, title="Key findings", icon=":material/insights:", url_path="findings", default=True)
COMPANIES = st.Page(companies.render, title="Taxi companies", icon=":material/local_taxi:", url_path="companies")
DROPOFFS = st.Page(dropoffs.render, title="Drop-off neighbourhoods", icon=":material/pin_drop:", url_path="dropoffs")
WEATHER = st.Page(weather.render, title="Rain and the airport run", icon=":material/rainy:", url_path="weather")
METHOD = st.Page(method.render, title="Data & method", icon=":material/dataset:", url_path="method")

PAGES = [FINDINGS, COMPANIES, DROPOFFS, WEATHER, METHOD]
