# 📚 Global Literacy & Education Trends — Analytical Study

> A data analytics capstone project exploring global literacy patterns, education trends, and their relationship with economic indicators from 1990 to 2023.

**GUVI × HCL Technologies Capstone Project**

---

## 📌 Project Overview

This project analyzes global literacy and education data sourced from [Our World in Data](https://ourworldindata.org), covering **158 countries** across **33 years** (1990–2023). It combines data engineering, SQL analysis, and an interactive Streamlit dashboard to uncover insights about literacy rates, gender gaps, schooling years, and GDP relationships worldwide.

---

## 🗂️ Project Structure

```
literacy_dashboard/
│
├── app.py                             # Streamlit dashboard (main application)
├── literacy.db                        # SQLite database (generated from Colab)
├── README.md                          # Project documentation
│
└── Global_Literacy_Analysis.ipynb     # Google Colab notebook
    ├── Data Collection
    ├── Data Cleaning
    ├── Feature Engineering
    ├── EDA (Exploratory Data Analysis)
    └── SQL Setup & Queries
```

---

## 📊 Dataset Sources

All data is sourced from [Our World in Data](https://ourworldindata.org):

| Dataset | Source |
|---|---|
| Adult Literacy Rate | `ourworldindata.org/grapher/literacy-rate-adults` |
| Youth Literacy (Male & Female) | `ourworldindata.org/grapher/literacy-rate-of-young-men-and-women` |
| Literate & Illiterate Population | `ourworldindata.org/grapher/literate-and-illiterate-world-population` |
| GDP per Capita (World Bank) | `ourworldindata.org/grapher/gdp-per-capita-worldbank` |
| Avg Years of Schooling | `ourworldindata.org/grapher/literacy-rates-vs-average-years-of-schooling` |

> **Note:** Literacy data has a natural 2–3 year publication lag as it is collected through UNESCO and World Bank national surveys. The most recent published data available is from **2023**.

---

## 🧱 Data Architecture

### 3 Master DataFrames

| DataFrame | Description | Key Columns |
|---|---|---|
| `df_literacy` | Adult & youth literacy with gender features | `adult_literacy`, `youth_male`, `youth_female`, `gender_gap`, `literacy_category` |
| `df_illiteracy` | Illiteracy rates by country and year | `illiteracy_pct`, `literacy_rate` |
| `df_gdp_schooling` | Economic and education indicators | `gdp_per_capita`, `avg_years_schooling`, `gdp_per_schooling_yr`, `gdp_category` |

### SQLite Database Tables

```
literacy_rates          →  from df_literacy
illiteracy_population   →  from df_illiteracy
gdp_schooling           →  from df_gdp_schooling
```

---

## ⚙️ Feature Engineering

12 features engineered from the raw data:

| Feature | Formula / Logic |
|---|---|
| `illiteracy_pct` | `100 - literacy_rate` |
| `gender_gap` | `youth_male - youth_female` |
| `gdp_per_schooling_yr` | `gdp_per_capita / avg_years_schooling` |
| `education_index` | `(adult_literacy/100 × 0.5) + (avg_years_schooling/20 × 0.5)` |
| `youth_literacy_avg` | `(youth_male + youth_female) / 2` |
| `literacy_growth_rate` | Year-over-year % change per country |
| `adult_youth_gap` | `youth_literacy_avg - adult_literacy` |
| `gender_parity_index` | `youth_female / youth_male` |
| `literacy_category` | Binned: Very Low / Low / Medium / High / Very High |
| `gdp_category` | Binned: Low / Lower Middle / Upper Middle / High Income |
| `schooling_efficiency` | `adult_literacy / avg_years_schooling` |
| `decade` | `(year // 10) × 10` |

---

## 🗄️ SQL Queries (13 Total)

| # | Query | Type |
|---|---|---|
| Q1 | Top 5 countries by adult literacy (2020) | Filter + Sort |
| Q2 | Countries with female youth literacy < 80% | Filter |
| Q3 | Average adult literacy per region | Group By |
| Q4 | Countries with illiteracy > 20% in 2000 | Filter |
| Q5 | India illiteracy trend (2000–2020) | Time Series |
| Q6 | Top 10 highest illiteracy % (latest year) | Subquery |
| Q7 | High schooling (>7 yrs) but low GDP (<$5000) | Multi-filter |
| Q8 | Rank countries by GDP per schooling year (2020) | Window Function |
| Q9 | Global average schooling years per year | Aggregate Trend |
| Q10 | High GDP but low schooling years (<6) in 2020 | Filter |
| Q11 | High illiteracy despite >10 schooling years | JOIN |
| Q12 | India literacy & GDP over 20 years | JOIN + Time Series |
| Q13 | Gender gap in high-GDP countries (2020) | JOIN + Filter |

---

## 🖥️ Streamlit Dashboard

### 4 Pages

| Page | Description |
|---|---|
| 🏠 **Home** | KPI cards, global literacy trend area chart, regional bar chart, world choropleth map |
| 🔍 **SQL Query Executor** | Run all 13 preset queries or write custom SQL — auto-generates best-fit chart per query |
| 📊 **EDA Visualizations** | 5 tabs: Trends · Correlations · Gender Gap · Rankings · World Map |
| 🌐 **Country Profile** | Per-country KPIs, dual-axis literacy & GDP chart, gender literacy, country vs global average |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google Colab (for generating the database)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/literacy_dashboard.git
cd literacy_dashboard
```

### 2. Install Dependencies

```bash
pip install streamlit plotly pandas sqlalchemy
```

### 3. Generate the SQLite Database

Open `Global_Literacy_Analysis.ipynb` in Google Colab and run all cells. Then download the generated database:

```python
from google.colab import files
files.download('literacy.db')
```

Place `literacy.db` inside the `literacy_dashboard/` folder.

### 4. Run the Dashboard

```bash
streamlit run app.py
```

App opens at → `http://localhost:8501`

---

## 🔬 Key Findings

- **Europe** has the highest average adult literacy globally; **Africa** shows the widest room for improvement
- Strong positive correlation **(r = 0.79)** between average years of schooling and adult literacy rate
- The global **gender literacy gap is closing** — the male-female gap has narrowed significantly since 1990
- **Higher GDP per capita** is strongly associated with higher literacy, but notable outliers exist
- **India** has made substantial progress, rising from ~48% adult literacy in 1990 to over 74% by 2020

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Pandas | Data cleaning & manipulation |
| Google Colab | Notebook for EDA and data pipeline |
| SQLite | Lightweight database storage |
| Streamlit | Interactive web dashboard |
| Plotly | Interactive charts and maps |
| Our World in Data | Primary data source |

---

## 👩‍💻 Author

**Luna**  
GUVI × HCL Technologies — Data Analytics Capstone  
March 2026

---

## 📄 License

This project is for educational purposes as part of the GUVI × HCL capstone program.  
Data sourced from Our World in Data is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
