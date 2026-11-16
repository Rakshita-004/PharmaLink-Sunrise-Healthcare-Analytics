# Project Report: Sunrise Healthcare Analytics
## Adapted PharmaLink Data Analytics Internship Project

### 1. Executive Summary
This project develops an integrated healthcare analytics solution using three supplied datasets: hospital resource utilisation (400 records), patient satisfaction (600 records) and appointments (2,000 records). The solution provides a reproducible data preparation process and an interactive Streamlit dashboard for monitoring operational resources, patient experience and appointment access.

### 2. Business Problem
Hospital managers need a consolidated view of capacity, service performance, patient feedback and appointment operations. Fragmented datasets make it difficult to identify service bottlenecks and operational improvement opportunities. This project addresses that need through descriptive analytics, data quality validation and interactive visual reporting.

### 3. Objectives
- Analyse hospital resource utilisation, staffing attendance, surgery activity and waiting time.
- Evaluate patient satisfaction across doctor, nurse, cleanliness and billing dimensions.
- Analyse appointment volume, no-show patterns, waiting time and consultation duration.
- Build an interactive dashboard with filters and management-level KPIs.
- Produce evidence-based recommendations while documenting data limitations.

### 4. Data Inventory
| Dataset | Records | Fields | Coverage |
|---|---:|---:|---|
| Resource utilisation | 400 | 14 | 2023–2024 |
| Patient satisfaction | 600 | 13 | 2023–2024 |
| Appointments | 2,000 | 15 | 2025–Jan 2026 |

The datasets have different grains and date coverage. They are analysed in separate subject areas rather than joined row-by-row.

### 5. Methodology
1. Load source CSV files using Pandas.
2. Inspect schemas, data types, date ranges, missing values and business-rule violations.
3. Parse dates and create explicit validation flags.
4. Derive capacity and operational measures only where denominators and source values are valid.
5. Explore distributions and trends by hospital, department, specialty and time.
6. Present metrics and charts through Streamlit and Plotly.

### 6. Initial Findings
- Appointment dataset: 2,000 records; observed no-show rate is 16.2% (324 records).
- Mean appointment waiting time is 35.23 minutes.
- Patient satisfaction dataset: mean overall satisfaction is 3.045 out of 5.
- Mean patient survey waiting time is 91.43 minutes.
- Resource dataset: mean recorded doctor attendance is 84.95%; mean nurse attendance is 87.42%; mean recorded waiting time is 78.66 minutes.
- Resource data has 175 records where occupied beds exceed total beds, 175 where ICU occupied beds exceed ICU capacity, and 182 where surgeries completed exceed surgeries scheduled. These are treated as data-quality issues and not silently corrected.
- 163 missing values in the satisfaction file are optional free-text feedback comments.

### 7. Dashboard
The dashboard contains four sections:
- Executive overview: headline metrics, coverage and data-quality warnings.
- Resource utilisation: valid bed/ICU occupancy measures, staffing and waiting-time trends.
- Patient satisfaction: rating dimensions, recommendation responses, department comparisons and comments.
- Appointments: appointment trends, specialty volumes and no-show analysis.

### 8. Recommendations
1. Review source-system validation for bed and ICU counts; enforce occupied capacity not exceeding total capacity.
2. Reconcile surgery scheduling and completion definitions to prevent impossible completion counts.
3. Investigate departments with high reported waiting times and lower satisfaction scores.
4. Segment appointment no-show rates by specialty, booking lead time, age group and insurance type to identify actionable patterns.
5. Consider reminder and confirmation workflows for appointments with higher no-show propensity, subject to operational validation.
6. Improve data integration by adding a consistent hospital identifier to appointment records.

### 9. Limitations
- No pharmaceutical SKU, sales, stock, batch or expiry data is supplied. Therefore pharmaceutical demand forecasting and medicine expiry alerts cannot be validated from these sources.
- Appointment data does not contain hospital identifiers; hospital-level appointment comparisons are not possible.
- Resource capacity data has substantial invalid records; occupancy averages must be interpreted cautiously.
- The datasets cover different periods and should not be treated as a unified longitudinal patient-level dataset.
- Findings are descriptive and do not establish causation.

### 10. Conclusion
The project delivers a practical healthcare analytics dashboard and data-quality workflow from the available source data. The solution supports management visibility into operational resources, patient experience and appointment performance. The next improvement step is to validate source-system definitions with stakeholders and obtain additional data for predictive modelling.
