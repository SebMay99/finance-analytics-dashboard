# Finance Analytics Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Web-0ea5e9)
![Status](https://img.shields.io/badge/Status-Active-22c55e)

> A Streamlit-based financial analytics tool that transforms Excel P&L models into interactive visual dashboards — enabling fast cost/revenue/margin analysis across business segments.

---

## Features

- **Multi-model loading** — upload and compare multiple Excel models simultaneously
- **Scenario analysis** — toggle between Day 1 and Growth projections
- **Segment views** — Products, Services, A&PS, or consolidated All view
- **Chart types** — Bar Charts and Donut Charts for Cost, Revenue, Margin, and FLGM%
- **Rebate analysis** — post-rebate Revenue and Margin% for Indirect sales motion models
- **Consolidated view** — merge all loaded models into a single aggregated dashboard
- **Export options** — save individual charts as PNG, all charts as ZIP, or the summary table as PNG/Excel
- **FX support** — automatic USD conversion via embedded exchange rate
- **Desktop build** — package as a standalone Windows `.exe` via PyInstaller

---

## Tech Stack

| Package | Purpose |
|---|---|
| `streamlit` | Web UI framework |
| `pandas` | DataFrame operations & Excel parsing |
| `plotly` | Interactive bar and donut charts |
| `openpyxl` | Excel file reading engine |
| `Pillow` | App icon loading |
| `kaleido` | Static PNG export from Plotly |
| `streamlit-desktop-app` | PyInstaller wrapper for `.exe` build |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Windows (for desktop build; web mode works cross-platform)

### Installation

```bash
git clone https://github.com/SebMay99/finance-analytics-dashboard.git
cd finance-analytics-dashboard

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### Desktop Build (Windows only)

```bat
build.bat
```

Produces a self-contained `.exe` in `dist/`.

---

## Usage

1. Launch the app and upload one or more Excel model files under **Data Ingestion**
2. Each file is loaded as an independent model identified by its filename
3. Use the **Select Model** dropdown to view individual models or a **Consolidated** view
4. Filter by **Scenario** (Day 1 / Growth), **View** (All / Products / Services / A&PS) and **Chart Style**
5. Download individual charts or all charts at once as a ZIP archive

---

## Excel File Format

The app reads Excel files with a sheet named **`PL_MGMT`** (or `PL_MGMT Edit` for custom edits).

### Required Sheet Layout

| Data | Row (1-based) | Columns |
|---|---|---|
| Sales Motion (`Direct` / `Indirect`) | Row 2 | Column I |
| Growth Revenue | Row 26 | B → X |
| Growth Cost | Row 28 | B → X |
| Growth Margin | Row 29 | B → X |
| Growth FLGM% | Row 30 | B → X |
| Growth Rebate Revenue *(Indirect only)* | Row 32 | G, R, S |
| Growth Rebate % *(Indirect only)* | Row 33 | G, R, S |
| Day 1 Revenue | Row 43 | B → X |
| Day 1 Cost | Row 45 | B → X |
| Day 1 Margin | Row 46 | B → X |
| Day 1 FLGM% | Row 47 | B → X |
| Day 1 Rebate Revenue *(Indirect only)* | Row 49 | G, R, S |
| Day 1 Rebate % *(Indirect only)* | Row 50 | G, R, S |
| Currency code | Row 54 | D |
| FX Rate (local / USD) | Row 55 | D |

### Category Columns (B → X, 23 values in order)

| # | Category | Group |
|---|---|---|
| 1 | HPC-AI | Products |
| 2 | Compute | Products |
| 3 | Storage | Products |
| 4 | Software | Products |
| 5 | 3P/OEM | Products |
| 6 | Total Product | Subtotal |
| 7 | Installation | Services |
| 8 | Support | Services |
| 9 | Complete Care | Services |
| 10 | Managed Services | Services |
| 11 | Colo | Services |
| 12 | 3PP Product | Services |
| 13 | 3PP Support | Services |
| 14 | SaaS | Services |
| 15 | SW Services | Services |
| 16 | Ezmeral | Services |
| 17 | Total Services | Subtotal |
| 18 | Total Products+Services | Subtotal |
| 19 | A&PS | A&PS |
| 20 | A&PS 3PP | A&PS |
| 21 | A&PS Colo | A&PS |
| 22 | Total A&PS | Subtotal |
| 23 | Grand Total | Grand Total |

---

## Sample Test Files

Pre-built test files are available in the `sample_data/` folder:

| File | Sales Motion | Currency |
|---|---|---|
| `direct_usd_sample.xlsx` | Direct | USD |
| `indirect_eur_sample.xlsx` | Indirect | EUR (with rebates) |

Use these to verify the app loads and renders correctly out of the box.

---

## Project Structure

```
finance-analytics-dashboard/
├── app.py                    # Main Streamlit entry point
├── build.bat                 # PyInstaller build script (Windows)
├── requirements.txt          # Python dependencies
├── style.css                 # Custom CSS theme
├── .streamlit/
│   └── config.toml           # Streamlit dark theme config
├── assets/
│   ├── app_icon.png          # App icon (build)
│   └── app_icon.webp         # App icon (runtime)
├── functions/
│   ├── processing.py         # Excel ingestion & data pipeline
│   ├── graphicator.py        # Plotly chart builders
│   └── download.py           # PNG/ZIP/Excel export logic
├── public/
│   └── config.py             # Category definitions & color maps
└── sample_data/
    ├── direct_usd_sample.xlsx
    └── indirect_eur_sample.xlsx
```

---

## Known Issues

- Occasional `numpy` initialization error on first launch of the desktop build. Closing and reopening resolves it.

---

## License

MIT
