# Sunrise Healthcare Analytics — Adapted PharmaLink Project

## Run locally (Windows PowerShell)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Project contents
- `app.py`: interactive Streamlit dashboard
- `data/raw/`: original supplied CSV files
- `data/processed/`: prepared/audited CSV copies
- `src/audit_data.py`: reproducible data validation and preparation
- `reports/`: project brief and initial audit outputs

## Dashboard tabs
1. Executive overview
2. Resource utilisation
3. Patient satisfaction
4. Appointments

## Important scope note
The original PharmaLink brief described pharmaceutical SKU demand forecasting and expiry-risk detection. The three supplied Sunrise files contain healthcare operations, satisfaction surveys and appointments—not medicine sales, inventory, batch or expiry records. This submission therefore implements a clearly labelled healthcare analytics adaptation and does not claim to deliver unsupported pharmaceutical features.

## Data quality notes
Resource utilisation data includes records where occupied beds exceed total beds, ICU occupancy exceeds capacity, and completed surgeries exceed scheduled surgeries. The dashboard flags these records and excludes invalid capacity rows from occupancy-rate averages. Appointment data has no hospital identifier and is analysed independently. Blank feedback comments are treated as optional missing text.


## Week 3 — Repeatable pipeline and baseline metrics
Run from the project root:
```powershell
python src/data_pipeline.py
```
Outputs:
- `data/processed/`: three processed CSV datasets with quality flags and derived measures.
- `reports/baseline_metrics.csv`: descriptive baseline KPIs.
- `reports/pipeline_quality_summary.json`: data-quality counts and pipeline checks.

To initialize Git version control (if Git is installed):
```powershell
git init
git add .
git commit -m "Week 3 data pipeline and baseline metrics"
```

## Week 9 – Dashboard V1 and Peer Review

### Dashboard Features

1. Executive Overview
2. Resource Utilisation
3. Patient Satisfaction
4. Appointment Analytics
5. Deep-dive Insights

### Interactive Features
- Hospital and department filters
- KPI cards and operational metrics
- Interactive Plotly visualizations
- Department-level comparisons
- Appointment no-show segmentation
- Data quality warnings

### Technology Stack
- Python
- Streamlit
- Pandas
- Plotly
- NumPy

### Dashboard Execution

Run the application using:

```bash
python -m streamlit run app.py
```

### Peer Review
The dashboard will undergo heuristic evaluation covering:
- Navigation and usability
- KPI clarity
- Chart readability
- Filter functionality
- Data reliability

Peer feedback and revisions will be documented separately.
