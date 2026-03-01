# HPE GreenLake Finance Analytics

A Streamlit-based financial analytics tool that transforms dense Excel financial models into interactive visual dashboards, enabling faster identification of cost optimization opportunities across GreenLake business segments.

> For the latest pre-built executable, see the [Releases](../../releases) page.

---

## Features

- Load and compare multiple financial models simultaneously
- Visualize Cost, Revenue, Margin and FLGM% breakdowns by segment
- Switch between Day 1 and Growth scenarios
- Support for Direct and Indirect sales motions (with post-rebate analysis)
- Consolidated view that correctly sums costs and recalculates FLGM%
- Export charts as PNG or ZIP archive

---

## Requirements

- Python 3.10+
- Windows (desktop build targets Windows only)

---

## Getting Started

### 1. Clone the repository

```bash
cd path/to/your/local/directory
git clone https://github.com/SebMay99/business-intelligence.git
cd business-intelligence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

```bash
.\.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Running Locally

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Building the Desktop Executable

The app can be packaged into a standalone `.exe` using the included build script:

```bash
.\build.bat
```

> Every file and asset referenced by the app must be explicitly declared in `build.bat`. Missing entries will cause the executable to fail at runtime.

The output will be located in the `dist/` folder.

---

## Project Structure

```
business-intelligence/
├── app.py                  # Main Streamlit application
├── build.bat               # PyInstaller build script
├── requirements.txt
├── style.css
├── functions/
│   ├── processing.py       # Data ingestion, transformation and consolidation
│   ├── graphicator.py      # Chart generation (bar and donut)
│   └── download.py         # PNG and ZIP export with native file dialogs
├── public/
│   └── config.py           # Category definitions and color mappings
└── assets/
    └── HPE_icon.webp
```

---

## Usage

1. Launch the app and upload one or more Excel model files under **Data Ingestion**
2. Each file is loaded as an independent model identified by its filename
3. Use the **Select Model** dropdown to view individual models or a **Consolidated** view that sums all loaded models
4. Filter by Scenario (Day 1 / Growth), View (All / Products / Services / A&PS) and Chart Style
5. Download individual charts or all charts at once as a ZIP archive

---

## Excel File Format

The app expects an Excel file with a sheet named `PL_MGMT` (or `PL_MGMT Edit` for custom files). The sheet must follow the standard GreenLake All Reports template.

| Field | Description |
|---|---|
| Sales Motion | Read from cell `I2` — either `Direct` or `Indirect` |
| Day 1 financials | Rows 42–46, columns B–X |
| Growth financials | Rows 25–29, columns B–X |
| Rebate data | Rows 31–32 and 48–49 (Indirect only) |

---

## Debugging Reference

### Example `filtered_table_df`

| Category | Cost | Revenue | Margin | Percentage |
|---|---|---|---|---|
| Compute | 230,127.50 | 482,650.50 | 252,523.00 | 52.32% |
| Storage | 8,319,115.00 | 35,422,830.00 | 27,103,720.00 | 76.51% |
| Total Product | 8,549,242.00 | 35,905,480.00 | 27,356,240.00 | 76.19% |
| Installation | 5,940.00 | 39,600.00 | 33,660.00 | 85.00% |
| Support | 364,351.70 | 2,010,798.00 | 1,646,447.00 | 81.88% |
| Complete Care | 356,912.30 | -1,653,450.00 | -2,010,362.00 | 121.59% |
| SaaS | 700.92 | 19,932.00 | 19,231.08 | 96.48% |
| Total Services | 727,904.90 | 416,880.50 | -311,024.50 | -74.61% |
| Pan HPE | 9,277,147.00 | 36,322,360.00 | 27,045,210.00 | 74.46% |

---

## Known Issues

- Occasional `numpy` initialization error on first launch of the desktop build. Closing and reopening the application resolves it.

---

## License

Internal use only — GreenLake Presales Team  
Contact: [sebastian.mayorga@hpe.com](mailto:sebastian.mayorga@hpe.com)