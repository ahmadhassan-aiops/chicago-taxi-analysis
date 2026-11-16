"""
Chicago taxi rides, November 2017: which companies and neighbourhoods dominate, and does rain slow the airport run?
An interactive presentation of Ahmad Hassan's SQL + Python analysis. All data ships with the app.
"""

import streamlit as st

st.set_page_config(
    page_title="Chicago taxi rides | Ahmad Hassan",
    page_icon=":material/local_taxi:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from lib.ui import inject_css  # noqa: E402
from nav import PAGES  # noqa: E402

inject_css()
st.navigation(PAGES, position="top").run()
