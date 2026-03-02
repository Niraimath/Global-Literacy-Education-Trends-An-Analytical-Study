# Global Literacy & Education Trends

An analytical study on global literacy rates and education indicators.

## What this does

Collects and cleans education data from Our World in Data, stores it in a SQLite database, and displays everything through an interactive Streamlit dashboard with Plotly charts.

## Stack

- Python, Pandas — data collection and cleaning
- SQLite — data storage and querying
- Streamlit + Plotly — interactive dashboard

## Getting started

**1. Run the Colab notebook first**

Open `Global_Literacy_and_Education_Analysis.ipynb` in Google Colab and run all cells. This downloads the datasets, cleans them, and creates `literacy.db`. Download the database file when done.

**2. Install dependencies**

```bash
pip install streamlit plotly pandas
```

**3. Run the app**

Place `literacy.db` in the same folder as `app.py`, then:

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

## Dashboard pages

- **Home** — global KPIs and world map
- **SQL Query Executor** — run any of the 13 preset queries or write your own
- **EDA Visualizations** — trends, correlations, gender gap, rankings, world map
- **Country Profile** — per-country breakdown with charts and comparisons

## Data sources

All data from [Our World in Data](https://ourworldindata.org), sourced from UNESCO and the World Bank. Most recent available year is 2023 due to the standard reporting lag on global education surveys.

## Notes

- The Colab notebook must be run before the dashboard — it generates the database
- Data collection uses a custom user-agent header to avoid 403 errors from OWID
