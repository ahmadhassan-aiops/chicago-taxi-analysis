"""
Offline build step: the three SQL result CSVs -> data/*.parquet + data/meta.json.

    python build_data.py "W:/Portfolio Projects/1. Data-analysis-with-python-Projects/Taxi Company Analysis"

The CSVs are the outputs of SQL queries on the Chicago taxi database:
  result_01: trips per taxi company in November 2017
  result_04: average daily drop-offs per Chicago neighbourhood in November 2017
  result_07: rides from the Loop to O'Hare airport on Saturdays in November 2017, with start hour, weather and duration
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

import pandas as pd

DEFAULT_RAW = Path("W:/Portfolio Projects/1. Data-analysis-with-python-Projects/Taxi Company Analysis")
OUT = Path(__file__).parent / "data"


def main(raw: Path) -> None:
    OUT.mkdir(exist_ok=True)
    companies = pd.read_csv(raw / "moved_project_sql_result_01.csv")
    dropoffs = pd.read_csv(raw / "moved_project_sql_result_04.csv")
    rides = pd.read_csv(raw / "moved_project_sql_result_07.csv", parse_dates=["start_ts"])
    shapes = {"companies": list(companies.shape), "dropoffs": list(dropoffs.shape), "rides": list(rides.shape)}

    companies = companies.sort_values("trips_amount", ascending=False, ignore_index=True)
    dropoffs = dropoffs.sort_values("average_trips", ascending=False, ignore_index=True)
    rides["duplicate"] = rides.duplicated()
    rides["hour"] = rides["start_ts"].dt.hour
    rides["date"] = rides["start_ts"].dt.date.astype(str)
    rides["minutes"] = rides["duration_seconds"] / 60

    companies.to_parquet(OUT / "companies.parquet", index=False)
    dropoffs.to_parquet(OUT / "dropoffs.parquet", index=False)
    rides.to_parquet(OUT / "rides.parquet", index=False)

    meta = {
        "built": date.today().isoformat(),
        "raw_shapes": shapes,
        "companies": int(len(companies)),
        "trips_total": int(companies["trips_amount"].sum()),
        "neighborhoods": int(len(dropoffs)),
        "rides": int(len(rides)),
        "duplicate_rides": int(rides["duplicate"].sum()),
        "zero_duration": int((rides["duration_seconds"] == 0).sum()),
        "saturdays": sorted(rides["date"].unique().tolist()),
        "distinct_start_times": int(rides["start_ts"].nunique()),
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RAW)
