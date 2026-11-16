"""Loads the prepared data in data/ and the weather-effect statistics."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from scipy import stats

DATA = Path(__file__).resolve().parent.parent / "data"


@st.cache_data
def meta() -> dict:
    return json.loads((DATA / "meta.json").read_text(encoding="utf-8"))


@st.cache_data
def table(name: str) -> pd.DataFrame:
    return pd.read_parquet(DATA / f"{name}.parquet")


@st.cache_data
def rides(drop_duplicates: bool = False, drop_zero: bool = True) -> pd.DataFrame:
    r = table("rides")
    if drop_duplicates:
        r = r[~r["duplicate"]]
    if drop_zero:
        r = r[r["duration_seconds"] > 0]
    return r.reset_index(drop=True)


def weather_effect_same_hour(r: pd.DataFrame) -> dict:
    """Least squares: minutes ~ bad weather + one dummy per start hour. Returns the weather coefficient."""
    bad = (r["weather_conditions"] == "Bad").astype(float)
    hours = pd.get_dummies(r["hour"], prefix="h", drop_first=True).astype(float)
    x = np.column_stack([np.ones(len(r)), bad.values, hours.values])
    y = r["minutes"].values
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta
    dof = len(y) - x.shape[1]
    cov = (resid @ resid / dof) * np.linalg.pinv(x.T @ x)
    se = float(np.sqrt(cov[1, 1]))
    t = float(beta[1] / se)
    h = stats.t.ppf(0.975, dof) * se
    return {"effect": float(beta[1]), "se": se, "p": float(2 * stats.t.sf(abs(t), dof)),
            "lo": float(beta[1] - h), "hi": float(beta[1] + h)}
