import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

BUILD_TAG = "vQA-TemplateA+B"

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(APP_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.append(SRC_DIR)

from metrics import (
    district_list, rainfall_by_district, rainfall_year_bounds, avg_rainfall_by_district,
    crop_state_list, crop_year_bounds, top_m_state_crops,
    latest_year_for_crop, district_extreme_for_crop
)

st.set_page_config(page_title="Samarth MVP – Rainfall & Crops", layout="wide")
st.title("Project Samarth – Rainfall & Top Crops (MVP)")
st.sidebar.write("BUILD:", BUILD_TAG)

tabs = st.tabs([
    "💧 Rainfall by District",
    "🌾 Top Crops by State",
    "🧠 Q&A (Template A)",
    "🧠 Q&A (Template B)"
])

def line_chart_matplotlib(x, y, xlabel="", ylabel="", title=""):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(x, y, marker="o")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title); ax.grid(True, alpha=0.3)
    st.pyplot(fig); plt.close(fig)

def bar_chart_matplotlib(labels, values, xlabel="", ylabel="", title=""):
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title); ax.grid(axis="y", alpha=0.3)
    plt.xticks(rotation=15, ha="right"); st.pyplot(fig); plt.close(fig)

# -------- Rainfall Tab --------
with tabs[0]:
    rf_path = os.path.join(APP_DIR, "data", "rainfall_clean.parquet")
    if not os.path.exists(rf_path):
        st.error("Missing data/rainfall_clean.parquet.")
    else:
        districts = district_list(); y_min, y_max = rainfall_year_bounds()
        c1, c2, c3 = st.columns([2,1,1])
        with c1: district = st.selectbox("Choose a district", districts, index=0)
        with c2: start_year = st.number_input("Start year", y_min, y_max, max(y_min, y_max-5), 1)
        with c3: end_year   = st.number_input("End year",   y_min, y_max, y_max, 1)
        if start_year <= end_year:
            rf = rainfall_by_district(district, start_year, end_year)
            if rf.empty: st.info("No rainfall data for that range.")
            else:
                st.subheader(f"Rainfall in {district} ({start_year}–{end_year})")
                st.dataframe(rf[["year","rainfall_mm"]], use_container_width=True)
                line_chart_matplotlib(rf["year"].tolist(), rf["rainfall_mm"].tolist(), "Year", "Rainfall (mm)", district)
        else: st.warning("Start year should be ≤ End year")
        st.caption("Rainfall source: data.gov.in (cleaned).")

with tabs[1]:
    cp_path = os.path.join(APP_DIR, "data", "crops_clean.parquet")
    if not os.path.exists(cp_path):
        st.error("Missing data/crops_clean.parquet.")
    else:
        states = crop_state_list(); cy_min, cy_max = crop_year_bounds()
        c1, c2, c3 = st.columns([2,1,1])
        with c1: state = st.selectbox("Choose a state", states, index=0, key="state_sel")
        with c2: cstart = st.number_input("Start year", cy_min, cy_max, max(cy_min, cy_max-5), 1, key="cstart")
        with c3: cend   = st.number_input("End year",   cy_min, cy_max, cy_max, 1, key="cend")
        m = st.slider("Top M crops", 1, 10, 5, 1)
        if cstart <= cend:
            top = top_m_state_crops(state, cstart, cend, m)
            if top.empty: st.info("No crop data for that range.")
            else:
                st.subheader(f"Top {m} crops in {state} ({cstart}–{cend})")
                st.dataframe(top, use_container_width=True)
                bar_chart_matplotlib(top["crop"].tolist(), top["production_tons"].tolist(), "Crop", "Production (tons)", state)
        else: st.warning("Start year should be ≤ End year")
        st.caption("Crop source: data.gov.in (cleaned).")

# -------- Q&A (Template A) --------
with tabs[2]:
    st.subheader("Compare rainfall (two districts) + Top crops (two states)")
    rf_ok = os.path.exists(os.path.join(APP_DIR, "data", "rainfall_clean.parquet"))
    cp_ok = os.path.exists(os.path.join(APP_DIR, "data", "crops_clean.parquet"))
    if not (rf_ok and cp_ok): st.error("Both rainfall and crops files required."); 
    else:
        districts = district_list(); states = crop_state_list()
        y_min, y_max = rainfall_year_bounds(); cy_min, cy_max = crop_year_bounds()
        a,b = st.columns(2)
        with a: d1 = st.selectbox("District A", districts, 0, key="qa_d1"); s1 = st.selectbox("State A", states, 0, key="qa_s1")
        with b: d2 = st.selectbox("District B", districts, 1 if len(districts)>1 else 0, key="qa_d2"); s2 = st.selectbox("State B", states, 1 if len(states)>1 else 0, key="qa_s2")
        c,d = st.columns(2)
        with c: N = st.number_input("Last N years (rainfall)", 1, (y_max-y_min+1), min(5,(y_max-y_min+1)))
        with d: M = st.number_input("Top M crops", 1, 10, 3)
        end_year = y_max; start_year = end_year - int(N) + 1
        if st.button("Run comparison (A)", type="primary"):
            r1 = rainfall_by_district(d1, start_year, end_year); r2 = rainfall_by_district(d2, start_year, end_year)
            st.markdown(f"### 🌧️ Rainfall ({start_year}–{end_year})")
            if r1.empty or r2.empty: st.info("Not enough rainfall data."); 
            else:
                c1, c2 = st.columns(2)
                with c1: line_chart_matplotlib(r1["year"].tolist(), r1["rainfall_mm"].tolist(), "Year", "Rainfall (mm)", d1)
                with c2: line_chart_matplotlib(r2["year"].tolist(), r2["rainfall_mm"].tolist(), "Year", "Rainfall (mm)", d2)
            st.markdown(f"### 🌾 Top {int(M)} crops (all available years)")
            top1 = top_m_state_crops(s1, cy_min, cy_max, int(M)); top2 = top_m_state_crops(s2, cy_min, cy_max, int(M))
            c1, c2 = st.columns(2)
            with c1:
                if top1.empty: st.info("No crop data for State A.")
                else: st.dataframe(top1, use_container_width=True); bar_chart_matplotlib(top1["crop"].tolist(), top1["production_tons"].tolist(), "Crop", "Production (tons)", s1)
            with c2:
                if top2.empty: st.info("No crop data for State B.")
                else: st.dataframe(top2, use_container_width=True); bar_chart_matplotlib(top2["crop"].tolist(), top2["production_tons"].tolist(), "Crop", "Production (tons)", s2)

with tabs[3]:
    st.subheader("Highest vs Lowest district production for a crop (latest year)")
    cp_ok = os.path.exists(os.path.join(APP_DIR, "data", "crops_clean.parquet"))
    if not cp_ok: st.error("Missing data/crops_clean.parquet.")
    else:
        states = crop_state_list()
        from loaders import load_crops
        crops_df = load_crops()
        crop_list = sorted(crops_df["crop"].dropna().astype(str).unique().tolist())

        a,b = st.columns(2)
        with a:
            sx = st.selectbox("State X (max)", states, 0, key="tb_sx")
            crop = st.selectbox("Crop", crop_list, 0, key="tb_crop")
        with b:
            sy = st.selectbox("State Y (min)", states, 1 if len(states)>1 else 0, key="tb_sy")

        if st.button("Find extremes (B)", type="primary"):
            yx = latest_year_for_crop(sx, crop)
            yy = latest_year_for_crop(sy, crop)

            if yx is None or yy is None:
                st.info("No data for that crop in one of the states.")
            else:
                mx = district_extreme_for_crop(sx, crop, yx, "max")
                mn = district_extreme_for_crop(sy, crop, yy, "min")

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{sx} – {crop} – Latest year: {yx}**")
                    if mx is None: st.info("Dataset may lack district-level details.")
                    else: st.success(f"Highest: **{mx['district']}** — {mx['production_tons']:,} tons")
                with col2:
                    st.write(f"**{sy} – {crop} – Latest year: {yy}**")
                    if mn is None: st.info("Dataset may lack district-level details.")
                    else: st.warning(f"Lowest: **{mn['district']}** — {mn['production_tons']:,} tons")

        with st.expander("Sources used (MVP)"):
            st.write("- Crops: data.gov.in crop production statistics (your cleaned file).")
