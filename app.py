import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

st.set_page_config(page_title="Global Literacy Dashboard", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
    .metric-card {
        background: linear-gradient(135deg, #0f172a, #1e293b);
        border: 1px solid #334155; border-radius: 16px;
        padding: 22px 16px; text-align: center;
    }
    .metric-value { font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; color: #60a5fa; }
    .metric-label { font-size: 0.78rem; color: #94a3b8; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.05em; }
    .stButton button {
        background: linear-gradient(135deg, #1d4ed8, #4f46e5) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


BASE = dict(
    paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
    font=dict(color='#e2e8f0', family='DM Sans'),
    title_font=dict(family='Syne', size=16, color='#f1f5f9'),
    margin=dict(l=40, r=40, t=55, b=40),
)

def style(fig, height=450):
    fig.update_layout(**BASE, height=height)
    fig.update_xaxes(gridcolor='#1e293b', zerolinecolor='#334155')
    fig.update_yaxes(gridcolor='#1e293b', zerolinecolor='#334155')
    return fig


@st.cache_data
def load_data():
    conn = sqlite3.connect('literacy.db')
    df_lit = pd.read_sql("SELECT * FROM literacy_rates", conn)
    df_ill = pd.read_sql("SELECT * FROM illiteracy_population", conn)
    df_gdp = pd.read_sql("SELECT * FROM gdp_schooling", conn)
    conn.close()
    for df in [df_lit, df_ill, df_gdp]:
        df['country'] = df['country'].str.strip().str.title()
    df_c = (
        df_lit
        .merge(df_gdp[['country','year','gdp_per_capita','avg_years_schooling','gdp_per_schooling_yr','gdp_category']], on=['country','year'], how='inner')
        .merge(df_ill[['country','year','illiteracy_pct']], on=['country','year'], how='left')
    )
    df_c['education_index'] = (df_c['adult_literacy']/100)*0.5 + (df_c['avg_years_schooling'].clip(upper=20)/20)*0.5
    return df_lit, df_ill, df_gdp, df_c

def run_query(q):
    conn = sqlite3.connect('literacy.db')
    r = pd.read_sql(q, conn)
    conn.close()
    return r

df_lit, df_ill, df_gdp, df_c = load_data()
MAX_YEAR = int(df_lit['year'].max())
MIN_YEAR = int(df_lit['year'].min())

#Sidebar 
st.sidebar.markdown(f"""
<div style='text-align:center; padding:10px 0 20px;'>
  <div style='font-size:2rem;'>📚</div>
  <div style='font-family:Syne; font-size:1.1rem; font-weight:800; color:#f1f5f9; margin-top:6px;'>Global Literacy & Education Trends:</div>
  <div style='font-size:0.72rem; color:#64748b; letter-spacing:0.08em; text-transform:uppercase;'>An Analytical Study</div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", ["🏠  Home","🔍  SQL Query Executor","📊  EDA Visualizations","🌐  Country Profile"])


# HOME

if page == "🏠  Home":
    st.markdown("<h1 style='font-size:2.4rem; color:#f1f5f9;'>Global Literacy & Education Trends: An Analytical Study</h1>", unsafe_allow_html=True)
    st.markdown("---")

    latest_lit = df_lit[df_lit['year'] == MAX_YEAR]
    latest_gdp = df_gdp[df_gdp['year'] == df_gdp['year'].max()]

    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in zip([c1,c2,c3,c4],
        [f"{latest_lit['adult_literacy'].mean():.1f}%", str(df_lit['country'].nunique()),
         f"${latest_gdp['gdp_per_capita'].mean():,.0f}", f"{latest_gdp['avg_years_schooling'].mean():.1f} yrs"],
        ["Avg Adult Literacy","Countries Tracked","Avg GDP per Capita","Avg Schooling Years"]):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        t = df_lit.groupby('year')['adult_literacy'].mean().reset_index()
        fig = px.area(t, x='year', y='adult_literacy', title='Global Avg Adult Literacy Over Time',
                      color_discrete_sequence=['#60a5fa'])
        fig.update_traces(fillcolor='rgba(96,165,250,0.1)', line_width=2.5)
        st.plotly_chart(style(fig), use_container_width=True)
    with col_b:
        if 'region' in df_lit.columns:
            r = df_lit.groupby('region')['adult_literacy'].mean().reset_index().sort_values('adult_literacy')
            fig2 = px.bar(r, x='adult_literacy', y='region', orientation='h',
                          title='Avg Adult Literacy by Region', color='adult_literacy',
                          color_continuous_scale='Blues', labels={'adult_literacy':'Literacy (%)','region':''})
            st.plotly_chart(style(fig2), use_container_width=True)

    if 'code' in df_lit.columns:
        fig3 = px.choropleth(latest_lit, locations='code', color='adult_literacy',
                             hover_name='country', color_continuous_scale='RdYlGn',
                             range_color=[20,100], title=f'World Adult Literacy Map ({MAX_YEAR})')
        st.plotly_chart(style(fig3, height=480), use_container_width=True)



elif page == "🔍  SQL Query Executor":
    st.markdown("<h1>🔍 SQL Query Executor</h1>", unsafe_allow_html=True)
    st.markdown("---")

    presets = {
        "— Write your own —": "",
        "Q1 — Top 5 highest adult literacy (2020)":
            "SELECT country, adult_literacy FROM literacy_rates WHERE year=2020 ORDER BY adult_literacy DESC LIMIT 5",
        "Q2 — Female youth literacy < 80%":
            "SELECT country, year, youth_female FROM literacy_rates WHERE youth_female < 80 ORDER BY youth_female",
        "Q3 — Avg adult literacy per region":
            "SELECT region, ROUND(AVG(adult_literacy),2) AS avg_literacy FROM literacy_rates GROUP BY region ORDER BY avg_literacy DESC",
        "Q4 — Illiteracy > 20% in 2000":
            "SELECT country, illiteracy_pct FROM illiteracy_population WHERE year=2000 AND illiteracy_pct>20 ORDER BY illiteracy_pct DESC",
        "Q5 — India illiteracy trend (2000–2020)":
            "SELECT year, illiteracy_pct FROM illiteracy_population WHERE country='India' AND year BETWEEN 2000 AND 2020 ORDER BY year",
        "Q6 — Top 10 largest illiteracy % (latest year)":
            "SELECT country, illiteracy_pct FROM illiteracy_population WHERE year=(SELECT MAX(year) FROM illiteracy_population) ORDER BY illiteracy_pct DESC LIMIT 10",
        "Q7 — High schooling (>7yrs) but low GDP (<5000)":
            "SELECT country, avg_years_schooling, gdp_per_capita FROM gdp_schooling WHERE avg_years_schooling>7 AND gdp_per_capita<5000 ORDER BY avg_years_schooling DESC",
        "Q8 — Rank by GDP per schooling year (2020)":
            "SELECT country, ROUND(gdp_per_schooling_yr,2) AS gdp_per_schooling_yr, RANK() OVER (ORDER BY gdp_per_schooling_yr DESC) AS rank FROM gdp_schooling WHERE year=2020",
        "Q9 — Global avg schooling per year":
            "SELECT year, ROUND(AVG(avg_years_schooling),2) AS global_avg FROM gdp_schooling GROUP BY year ORDER BY year",
        "Q10 — High GDP but low schooling (<6yrs) in 2020":
            "SELECT country, gdp_per_capita, avg_years_schooling FROM gdp_schooling WHERE year=2020 AND avg_years_schooling<6 ORDER BY gdp_per_capita DESC LIMIT 10",
        "Q11 — High illiteracy despite >10 schooling years":
            "SELECT i.country, i.year, i.illiteracy_pct, g.avg_years_schooling FROM illiteracy_population i JOIN gdp_schooling g ON i.country=g.country AND i.year=g.year WHERE g.avg_years_schooling>10 AND i.illiteracy_pct>10 ORDER BY i.illiteracy_pct DESC",
        "Q12 — India literacy & GDP over 20 years":
            "SELECT l.year, l.adult_literacy, g.gdp_per_capita FROM literacy_rates l JOIN gdp_schooling g ON l.country=g.country AND l.year=g.year WHERE l.country='India' ORDER BY l.year",
        "Q13 — Gender gap in high-GDP countries (2020)":
            "SELECT l.country, l.youth_male, l.youth_female, ROUND(l.youth_male-l.youth_female,2) AS gender_gap, g.gdp_per_capita FROM literacy_rates l JOIN gdp_schooling g ON l.country=g.country AND l.year=g.year WHERE g.year=2020 AND g.gdp_per_capita>30000 ORDER BY gender_gap DESC",
    }

    smart = {
        "Q1 — Top 5 highest adult literacy (2020)":          ("bar_h",  "country",             "adult_literacy"),
        "Q2 — Female youth literacy < 80%":                  ("scatter","year",                 "youth_female"),
        "Q3 — Avg adult literacy per region":                ("bar_h",  "region",               "avg_literacy"),
        "Q4 — Illiteracy > 20% in 2000":                     ("bar_h",  "country",              "illiteracy_pct"),
        "Q5 — India illiteracy trend (2000–2020)":           ("line",   "year",                 "illiteracy_pct"),
        "Q6 — Top 10 largest illiteracy % (latest year)":    ("bar_h",  "country",              "illiteracy_pct"),
        "Q7 — High schooling (>7yrs) but low GDP (<5000)":   ("scatter","avg_years_schooling",  "gdp_per_capita"),
        "Q8 — Rank by GDP per schooling year (2020)":        ("bar_h",  "country",              "gdp_per_schooling_yr"),
        "Q9 — Global avg schooling per year":                ("line",   "year",                 "global_avg"),
        "Q10 — High GDP but low schooling (<6yrs) in 2020":  ("scatter","avg_years_schooling",  "gdp_per_capita"),
        "Q11 — High illiteracy despite >10 schooling years": ("scatter","avg_years_schooling",  "illiteracy_pct"),
        "Q12 — India literacy & GDP over 20 years":          ("dual",   "year",                 "adult_literacy"),
        "Q13 — Gender gap in high-GDP countries (2020)":     ("bar_h",  "country",              "gender_gap"),
    }

    selected = st.selectbox("Choose a preset query", list(presets.keys()))
    query    = st.text_area("✏️ SQL Query", value=presets[selected], height=100)

    if st.button("▶️ Run Query", type="primary"):
        if query.strip():
            try:
                st.session_state['sql_result']   = run_query(query)
                st.session_state['sql_selected'] = selected
            except Exception as e:
                st.error(f"Query error: {e}")
        else:
            st.warning("Please enter a query.")

    if 'sql_result' in st.session_state:
        df_r  = st.session_state['sql_result']
        sel_q = st.session_state.get('sql_selected', '')
        st.success(f"✅ {len(df_r)} rows returned")
        st.markdown("---")
        st.markdown("#### 📋 Result Table")
        st.dataframe(df_r, use_container_width=True, height=min(380, 60+len(df_r)*38))
        st.markdown("---")
        st.markdown("#### 📊 Chart")

        num_cols = df_r.select_dtypes(include='number').columns.tolist()
        cat_cols = df_r.select_dtypes(exclude='number').columns.tolist()

        if num_cols:
            s_type, s_x, s_y = smart.get(sel_q, ("bar_h", cat_cols[0] if cat_cols else num_cols[0], num_cols[0]))
            all_cols = cat_cols + num_cols
            def_x = s_x if s_x in df_r.columns else (cat_cols[0] if cat_cols else num_cols[0])
            def_y = s_y if s_y in df_r.columns else num_cols[0]
            type_map = {"bar_h":"Horizontal Bar","line":"Line"}
            def_type = type_map.get(s_type, "Horizontal Bar")
            chart_opts = ["Horizontal Bar","Vertical Bar","Line","Pie"]

            k1, k2, k3 = st.columns(3)
            with k1:
                ct = st.selectbox("Chart type", chart_opts,
                                  index=chart_opts.index(def_type) if def_type in chart_opts else 0, key="ct")
            with k2:
                xc = st.selectbox("X axis", all_cols,
                                  index=all_cols.index(def_x) if def_x in all_cols else 0, key="xc")
            with k3:
                yc = st.selectbox("Y axis", num_cols,
                                  index=num_cols.index(def_y) if def_y in num_cols else 0, key="yc")

            title = f"{yc.replace('_',' ').title()} by {xc.replace('_',' ').title()}"

            if ct == "Horizontal Bar":
                fig = px.bar(df_r, x=yc, y=xc, orientation='h', color=yc,
                             color_continuous_scale='Blues', text=yc, title=title)
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_yaxes(autorange='reversed')
                style(fig, height=max(420, len(df_r)*42))

            elif ct == "Vertical Bar":
                fig = px.bar(df_r, x=xc, y=yc, color=yc,
                             color_continuous_scale='Teal', text=yc, title=title)
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                style(fig, height=480)

            elif ct == "Line":
                fig = px.line(df_r, x=xc, y=yc, markers=True, title=title,
                              color_discrete_sequence=['#60a5fa'])
                fig.update_traces(line_width=3, marker_size=8)
                style(fig, height=480)

            elif ct == "Pie":
                fig = px.pie(df_r, names=xc, values=yc, hole=0.45, title=title,
                             color_discrete_sequence=px.colors.qualitative.Bold)
                fig.update_traces(textposition='outside', textinfo='percent+label')
                style(fig, height=500)

            st.plotly_chart(fig, use_container_width=True)

#EDA VISUALIZATIONS

elif page == "📊  EDA Visualizations":
    st.markdown("<h1>📊 EDA Visualizations</h1>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Trends","🔗 Correlations","⚧ Gender Gap","🏆 Rankings","🗺️ World Map"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            t = df_lit.groupby('year')['adult_literacy'].mean().reset_index()
            fig = px.area(t, x='year', y='adult_literacy', title='Global Avg Adult Literacy Over Time',
                          color_discrete_sequence=['#60a5fa'])
            fig.update_traces(fillcolor='rgba(96,165,250,0.1)', line_width=2.5)
            st.plotly_chart(style(fig), use_container_width=True)
        with c2:
            t2 = df_gdp.groupby('year')['avg_years_schooling'].mean().reset_index()
            fig2 = px.area(t2, x='year', y='avg_years_schooling', title='Global Avg Schooling Years Over Time',
                           color_discrete_sequence=['#a78bfa'])
            fig2.update_traces(fillcolor='rgba(167,139,250,0.1)', line_width=2.5)
            st.plotly_chart(style(fig2), use_container_width=True)

        if 'literacy_rate' in df_ill.columns and 'illiteracy_pct' in df_ill.columns:
            il = df_ill.groupby('year')[['literacy_rate','illiteracy_pct']].mean().reset_index()
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=il['year'], y=il['literacy_rate'], name='Literacy Rate',
                                      fill='tozeroy', line=dict(color='#34d399', width=2.5),
                                      fillcolor='rgba(52,211,153,0.12)'))
            fig3.add_trace(go.Scatter(x=il['year'], y=il['illiteracy_pct'], name='Illiteracy Rate',
                                      fill='tozeroy', line=dict(color='#f87171', width=2.5),
                                      fillcolor='rgba(248,113,113,0.12)'))
            fig3.update_layout(title='Literacy vs Illiteracy Rate Over Time',
                               xaxis_title='Year', yaxis_title='Rate (%)', **BASE)
            fig3.update_xaxes(gridcolor='#1e293b')
            fig3.update_yaxes(gridcolor='#1e293b')
            st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        yr_opts = sorted(df_c['year'].unique())
        yr = st.slider("Select Year", int(min(yr_opts)), int(max(yr_opts)), int(max(yr_opts)))
        df_yr = df_c[df_c['year']==yr].dropna(subset=['gdp_per_capita','adult_literacy'])

        c1, c2 = st.columns(2)
        with c1:
            fig = px.scatter(df_yr, x='gdp_per_capita', y='adult_literacy', hover_name='country',
                             color='region' if 'region' in df_yr.columns else 'adult_literacy',
                             trendline='ols', title=f'GDP vs Adult Literacy ({yr})',
                             labels={'gdp_per_capita':'GDP ($)','adult_literacy':'Literacy (%)'})
            st.plotly_chart(style(fig), use_container_width=True)
        with c2:
            df_sc = df_c[df_c['year']==yr].dropna(subset=['avg_years_schooling','adult_literacy'])
            fig2 = px.scatter(df_sc, x='avg_years_schooling', y='adult_literacy', hover_name='country',
                              color='region' if 'region' in df_sc.columns else 'adult_literacy',
                              trendline='ols', title=f'Schooling Years vs Literacy ({yr})',
                              labels={'avg_years_schooling':'Avg Schooling Yrs','adult_literacy':'Literacy (%)'})
            st.plotly_chart(style(fig2), use_container_width=True)

        corr_cols = [c for c in ['adult_literacy','youth_male','youth_female','gender_gap',
                                  'gdp_per_capita','avg_years_schooling','education_index']
                     if c in df_c.columns]
        corr = df_c[corr_cols].corr().round(2)
        fig3 = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r',
                         title='Correlation Heatmap — Key Indicators', aspect='auto')
        st.plotly_chart(style(fig3, height=500), use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            gy = st.selectbox("Year", sorted(df_lit['year'].unique(), reverse=True), key='gy')
            top_gap = df_lit[df_lit['year']==gy].dropna(subset=['gender_gap']).nlargest(15,'gender_gap')
            fig = px.bar(top_gap, x='gender_gap', y='country', orientation='h',
                         color='gender_gap', color_continuous_scale='RdBu',
                         title=f'Top 15 Gender Literacy Gap ({gy})',
                         labels={'gender_gap':'Male − Female (%)','country':''})
            fig.update_yaxes(autorange='reversed')
            st.plotly_chart(style(fig, height=500), use_container_width=True)
        with c2:
            gt = df_lit.groupby('year')['gender_gap'].mean().reset_index()
            fig2 = px.line(gt, x='year', y='gender_gap', markers=True,
                           title='Global Gender Gap Closing Over Time',
                           color_discrete_sequence=['#f472b6'])
            fig2.update_traces(line_width=3, marker_size=7)
            fig2.add_hline(y=0, line_dash='dash', line_color='#64748b', annotation_text='Parity')
            st.plotly_chart(style(fig2), use_container_width=True)

        fig3 = px.scatter(df_lit.dropna(subset=['youth_male','youth_female']),
                          x='youth_male', y='youth_female', hover_name='country', opacity=0.6,
                          color='region' if 'region' in df_lit.columns else 'adult_literacy',
                          trendline='ols', title='Youth Male vs Female Literacy by Region',
                          labels={'youth_male':'Male (%)','youth_female':'Female (%)'})
        fig3.add_shape(type='line', x0=20, y0=20, x1=100, y1=100,
                       line=dict(color='#64748b', dash='dot', width=1.5))
        st.plotly_chart(style(fig3, height=500), use_container_width=True)

    with tab4:
        ry = st.selectbox("Year", sorted(df_lit['year'].unique(), reverse=True), key='ry')
        c1, c2 = st.columns(2)
        with c1:
            top20 = df_lit[df_lit['year']==ry].nlargest(20,'adult_literacy')
            fig = px.bar(top20, x='adult_literacy', y='country', orientation='h',
                         color='adult_literacy', color_continuous_scale='Greens',
                         title=f'Top 20 — Adult Literacy ({ry})', text='adult_literacy')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_yaxes(autorange='reversed')
            st.plotly_chart(style(fig, height=600), use_container_width=True)
        with c2:
            bot20 = df_lit[df_lit['year']==ry].nsmallest(20,'adult_literacy')
            fig2 = px.bar(bot20, x='adult_literacy', y='country', orientation='h',
                          color='adult_literacy', color_continuous_scale='Reds_r',
                          title=f'Bottom 20 — Adult Literacy ({ry})', text='adult_literacy')
            fig2.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig2.update_yaxes(autorange='reversed')
            st.plotly_chart(style(fig2, height=600), use_container_width=True)

    with tab5:
        my = st.slider("Year", MIN_YEAR, MAX_YEAR, MAX_YEAR, key='my')
        mm_options = [c for c in ['adult_literacy','gender_gap','youth_literacy_avg'] if c in df_lit.columns]
        mm = st.selectbox("Metric", mm_options, format_func=lambda x: x.replace('_',' ').title())
        df_map = df_lit[df_lit['year']==my].dropna(subset=[mm])
        if not df_map.empty and 'code' in df_map.columns:
            fig = px.choropleth(df_map, locations='code', color=mm, hover_name='country',
                                color_continuous_scale='RdYlGn',
                                title=f'{mm.replace("_"," ").title()} — {my}')
            st.plotly_chart(style(fig, height=540), use_container_width=True)
        else:
            st.info("No map data for this selection.")

#COUNTRY PROFILE

elif page == "🌐  Country Profile":
    st.markdown("<h1>🌐 Country Profile</h1>", unsafe_allow_html=True)
    st.markdown("---")

    countries = sorted(df_c['country'].unique())
    country   = st.selectbox("Select a Country", countries,
                              index=countries.index('India') if 'India' in countries else 0)
    df_co     = df_c[df_c['country'] == country].sort_values('year')

    if df_co.empty:
        st.warning("No data for this country.")
    else:
        latest = df_co.iloc[-1]
        st.markdown(f"<h3 style='color:#60a5fa;'>📌 {country} · Latest: {int(latest['year'])}</h3>", unsafe_allow_html=True)
        st.markdown("---")

        c1,c2,c3,c4,c5 = st.columns(5)
        kpi_vals = [
            (f"{latest['adult_literacy']:.1f}%"        if pd.notna(latest.get('adult_literacy'))      else 'N/A', "Adult Literacy"),
            (f"{latest['youth_male']:.1f}%"             if pd.notna(latest.get('youth_male'))           else 'N/A', "Youth Male"),
            (f"{latest['youth_female']:.1f}%"           if pd.notna(latest.get('youth_female'))         else 'N/A', "Youth Female"),
            (f"${latest['gdp_per_capita']:,.0f}"        if pd.notna(latest.get('gdp_per_capita'))       else 'N/A', "GDP per Capita"),
            (f"{latest['avg_years_schooling']:.1f} yrs" if pd.notna(latest.get('avg_years_schooling')) else 'N/A', "Avg Schooling"),
        ]
        for col, (val, label) in zip([c1,c2,c3,c4,c5], kpi_vals):
            with col:
                st.markdown(f'<div class="metric-card"><div class="metric-value" style="font-size:1.4rem">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_co['year'], y=df_co['adult_literacy'],
                                     name='Adult Literacy (%)', mode='lines+markers',
                                     line=dict(color='#60a5fa', width=3)))
            if 'gdp_per_capita' in df_co.columns:
                fig.add_trace(go.Scatter(x=df_co['year'], y=df_co['gdp_per_capita'],
                                         name='GDP per Capita ($)', yaxis='y2', mode='lines+markers',
                                         line=dict(color='#fbbf24', width=3, dash='dash')))
            fig.update_layout(
                 title=f'{country} — Literacy & GDP Over Time',
                 yaxis=dict(title='Literacy (%)', color='#60a5fa', gridcolor='#1e293b'),
                 yaxis2=dict(title='GDP ($)', overlaying='y', side='right', color='#fbbf24', gridcolor='#1e293b'),
                 legend=dict(orientation='h', bgcolor='rgba(0,0,0,0)'),
                 paper_bgcolor='#0f172a', plot_bgcolor='#0f172a',
                 font=dict(color='#e2e8f0', family='DM Sans'),
                 title_font=dict(family='Syne', size=16, color='#f1f5f9'),
                 margin=dict(l=40, r=40, t=55, b=40),
                 height=420
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=df_co['year'], y=df_co['youth_male'], name='Youth Male',
                                      fill='tozeroy', line=dict(color='#60a5fa', width=2.5),
                                      fillcolor='rgba(96,165,250,0.12)'))
            fig2.add_trace(go.Scatter(x=df_co['year'], y=df_co['youth_female'], name='Youth Female',
                                      fill='tozeroy', line=dict(color='#f472b6', width=2.5),
                                      fillcolor='rgba(244,114,182,0.12)'))
            fig2.update_layout(title=f'{country} — Youth Literacy by Gender',
                               yaxis_title='Literacy (%)', **BASE, height=420)
            fig2.update_xaxes(gridcolor='#1e293b')
            fig2.update_yaxes(gridcolor='#1e293b')
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            fig3 = px.area(df_co.dropna(subset=['avg_years_schooling']), x='year', y='avg_years_schooling',
                           title=f'{country} — Avg Years of Schooling',
                           color_discrete_sequence=['#a78bfa'])
            fig3.update_traces(fillcolor='rgba(167,139,250,0.1)', line_width=2.5)
            st.plotly_chart(style(fig3, height=380), use_container_width=True)

        with c4:
            df_il = df_ill[df_ill['country'] == country].sort_values('year')
            if not df_il.empty and 'illiteracy_pct' in df_il.columns:
                fig4 = px.bar(df_il, x='year', y='illiteracy_pct', color='illiteracy_pct',
                              color_continuous_scale='Reds_r',
                              title=f'{country} — Illiteracy Rate Over Time')
                st.plotly_chart(style(fig4, height=380), use_container_width=True)
            else:
                st.info("No illiteracy data for this country.")

        st.markdown("#### 📊 Country vs Global Average")
        yr = int(latest['year'])
        g_avg = df_c[df_c['year']==yr][['adult_literacy','youth_male','youth_female','gdp_per_capita','avg_years_schooling']].mean()
        cmp = pd.DataFrame({
            'Metric': ['Adult Literacy','Youth Male','Youth Female','GDP per Capita','Avg Schooling'],
            country:  [latest.get('adult_literacy'), latest.get('youth_male'), latest.get('youth_female'),
                       latest.get('gdp_per_capita'), latest.get('avg_years_schooling')],
            'Global Avg': g_avg.values
        })
        fig5 = px.bar(cmp, x='Metric', y=[country,'Global Avg'], barmode='group',
                      title=f'{country} vs Global Average ({yr})',
                      color_discrete_sequence=['#60a5fa','#34d399'])
        st.plotly_chart(style(fig5, height=420), use_container_width=True)

        st.markdown("#### 📋 Full Data Table")
        st.dataframe(df_co.reset_index(drop=True), use_container_width=True)