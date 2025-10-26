# Project Samarth – Intelligent Q&A over India’s Agriculture & Climate Data

A minimal, end-to-end prototype that answers questions about India’s agricultural economy and climate patterns using public data from **data.gov.in** (IMD + MoA&FW).  
Built with **Streamlit + pandas**; designed to be **local-first** and **privacy-friendly**.

> 🎥 **Demo (2 min):** https://www.loom.com/share/f875469b02684a07b127d49c8adce70a

---

## ✨ Features
- **💧 Rainfall explorer (district)** — view annual rainfall trends for any district and year range.
- **🌾 Top crops explorer (state)** — see the top *M* crops by production over a selected window.
- **🧠 Q&A – Template A** — compare average rainfall of two districts (last *N* years) + top crops of two states.
- **🧠 Q&A – Template B** — find the **highest** production district for a crop in *State X* (latest year) and compare with the **lowest** in *State Y*.

---

## 🗺️ Data Sources (data.gov.in)
- **Rainfall (IMD)**: District/State rainfall tables (cleaned to `district, year, rainfall_mm`).
- **Crop Production (MoA&FW)**: State/District crop production (normalized to `state, district?, crop, year, production_tons`).

> This repo **excludes big data files** to keep it small. Place your cleaned files locally in `data/` (see “Setup”).

---

## 🧰 Tech Stack
- **Python**, **Streamlit**, **pandas**, **matplotlib**, **pyarrow**
- Local files (Parquet) for fast, reproducible queries
