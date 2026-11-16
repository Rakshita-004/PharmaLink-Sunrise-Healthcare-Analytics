# Sunrise Healthcare Analytics — Adapted Project Brief

## Project context
This is an adapted analytics project using the three supplied Sunrise healthcare datasets. The supplied data describes hospital resource utilisation, patient satisfaction and appointments. It does not describe pharmaceutical SKU sales, stock on hand, batches or expiry dates.

## Business objective
Develop an integrated analytics solution to help healthcare management:
1. Monitor bed and ICU utilisation, surgeries, staffing attendance, waiting times and readmissions.
2. Understand patient satisfaction across service dimensions and identify recurring feedback themes.
3. Analyse appointment volumes, no-show patterns, waiting times and consultation durations.
4. Provide interactive dashboards and evidence-based operational recommendations.

## Scope and limitations
- Do not claim pharmaceutical demand forecasting or medicine expiry-risk detection from these files.
- Appointment records do not contain a hospital identifier; do not attribute appointments to Sunrise hospital locations.
- Resource records contain invalid capacity/completion relationships that must be investigated and flagged before KPI publication.
- Missing patient feedback comments are treated as optional text, not automatically as missing survey responses.
- The datasets cover different time periods; cross-dataset comparisons must respect date coverage and aggregation level.

## Technology plan
Python, Pandas, NumPy, Plotly, Streamlit, Scikit-learn (where predictive modelling is justified), and MLflow for experiment tracking if predictive experiments are implemented.

## Official milestone mapping
- Week 1: Stakeholder brief + data inventory.
- Week 3: Data pipeline + baseline metrics.
- Week 6: Deep-dive analysis.
- Week 9: Dashboard v1 + peer review.
- Week 12: Final dashboard + strategic brief.

## Initial success measures
- Reproducible data ingestion and validation.
- Transparent data-quality flags and documented exclusions.
- Correctly defined operational and patient-experience KPIs.
- Interactive filters and drill-downs where the data supports them.
- Recommendations traceable to analysis.
