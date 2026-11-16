# Chicago taxis: who wins the market, where rides end, and does rain slow the airport run?

An interactive presentation of a SQL + Python analysis by **Ahmad Hassan** (AI Engineer), for a ride-sharing
company preparing to launch in Chicago. SQL queries on Chicago taxi trips and weather data (November 2017)
produced three result tables; Python analyses them.

- **Key findings** and launch recommendations.
- **Taxi companies**: trips per company and how concentrated the market is.
- **Drop-off neighbourhoods**: where rides end.
- **Rain and the airport run**: Welch's t-test on Loop to O'Hare ride durations, then the same comparison at the
  same start hour (regression with hour terms), with toggles for the cleaning choices.
- **Data & method**: the SQL results, cleaning decisions, test design and limits.

Notebook (updated with the corrections described in the app): [AIOPS-Portfolio-Projects / Taxi Company Analysis](https://github.com/ahmadhassan-aiops/AIOPS-Portfolio-Projects/tree/main/1.%20Data-analysis-with-python-Projects/Taxi%20Company%20Analysis)

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Rebuild the data: `python build_data.py "path/to/Taxi Company Analysis"` (folder with the three
`moved_project_sql_result_*.csv` files).

Structure: `app.py` (entry), `nav.py` (pages), `views/` (one module per page), `lib/` (data loading, statistics,
charts, UI), `build_data.py` (CSVs to Parquet), `data/` (shipped with the app), `Dockerfile` (port 7860).
