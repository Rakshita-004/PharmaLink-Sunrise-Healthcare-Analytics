"""Week 6 deep-dive analysis for Sunrise Healthcare Analytics.
Run from project root: python src/deep_dive_analysis.py
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, kruskal, chi2_contingency
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
RAW, REPORTS = ROOT / "data" / "raw", ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

r = pd.read_csv(RAW / "sunrise_resource_utilisation.csv", parse_dates=["date"])
s = pd.read_csv(RAW / "sunrise_patient_satisfaction.csv", parse_dates=["survey_date"])
a = pd.read_csv(RAW / "da_healthcare_appointments.csv", parse_dates=["booking_date", "appointment_date"])

# Resource analysis: invalid capacity values are excluded from utilization calculations.
r["bed_valid"] = (r.total_beds > 0) & (r.occupied_beds >= 0) & (r.occupied_beds <= r.total_beds)
r["icu_valid"] = (r.icu_beds_total > 0) & (r.icu_beds_occupied >= 0) & (r.icu_beds_occupied <= r.icu_beds_total)
r["bed_occupancy_pct"] = (r.occupied_beds / r.total_beds * 100).where(r.bed_valid)
r["icu_occupancy_pct"] = (r.icu_beds_occupied / r.icu_beds_total * 100).where(r.icu_valid)
r["surgery_valid"] = (r.surgeries_scheduled >= 0) & (r.surgeries_completed >= 0) & (r.surgeries_completed <= r.surgeries_scheduled)
r["surgery_completion_pct"] = (r.surgeries_completed / r.surgeries_scheduled * 100).where(r.surgery_valid & (r.surgeries_scheduled > 0))

r.groupby("hospital").agg(
    records=("record_id", "count"), valid_bed_records=("bed_valid", "sum"),
    mean_bed_occupancy_pct=("bed_occupancy_pct", "mean"),
    valid_icu_records=("icu_valid", "sum"), mean_icu_occupancy_pct=("icu_occupancy_pct", "mean"),
    mean_doctor_attendance_pct=("doctor_attendance_pct", "mean"),
    mean_nurse_attendance_pct=("nurse_attendance_pct", "mean"),
    mean_wait_mins=("avg_patient_wait_mins", "mean"),
    total_readmissions=("readmission_count", "sum")
).reset_index().to_csv(REPORTS / "deepdive_resource_by_hospital.csv", index=False)

r.groupby("department").agg(
    records=("record_id", "count"), valid_bed_records=("bed_valid", "sum"),
    mean_bed_occupancy_pct=("bed_occupancy_pct", "mean"),
    mean_wait_mins=("avg_patient_wait_mins", "mean"),
    mean_doctor_attendance_pct=("doctor_attendance_pct", "mean"),
    mean_nurse_attendance_pct=("nurse_attendance_pct", "mean"),
    invalid_surgery_records=("surgery_valid", lambda x: int((~x).sum()))
).reset_index().to_csv(REPORTS / "deepdive_resource_by_department.csv", index=False)

resource_corr = []
for col in ["doctor_attendance_pct", "nurse_attendance_pct", "bed_occupancy_pct", "icu_occupancy_pct"]:
    pair = pd.DataFrame({"x": r[col], "y": r.avg_patient_wait_mins}).dropna()
    rho, p = spearmanr(pair.x, pair.y)
    resource_corr.append({"variable": col, "outcome": "avg_patient_wait_mins", "n": len(pair), "spearman_rho": rho, "p_value": p})
pd.DataFrame(resource_corr).to_csv(REPORTS / "deepdive_resource_correlations.csv", index=False)

# Satisfaction: ordinal associations and department comparison.
sat_corr = []
for col in ["doctor_rating", "nurse_rating", "cleanliness_rating", "billing_clarity_rating", "waiting_time_mins"]:
    rho, p = spearmanr(s[col], s.overall_satisfaction)
    sat_corr.append({"variable": col, "outcome": "overall_satisfaction", "n": len(s), "spearman_rho": rho, "p_value": p})
pd.DataFrame(sat_corr).to_csv(REPORTS / "deepdive_satisfaction_correlations.csv", index=False)

s.groupby("department").agg(
    surveys=("survey_id", "count"),
    mean_overall_satisfaction=("overall_satisfaction", "mean"),
    median_overall_satisfaction=("overall_satisfaction", "median"),
    mean_wait_mins=("waiting_time_mins", "mean"),
    recommend_yes_pct=("would_recommend", lambda x: (x == "Yes").mean() * 100)
).reset_index().to_csv(REPORTS / "deepdive_satisfaction_by_department.csv", index=False)
groups = [g.overall_satisfaction.values for _, g in s.groupby("department") if len(g) >= 2]
kw = kruskal(*groups)

# Appointment cohorts and segments. The supplied dates produce lead times of 1–14 days.
a["lead_time_days"] = (a.appointment_date - a.booking_date).dt.days
a["lead_time_cohort"] = pd.cut(a.lead_time_days, [-1, 0, 3, 7, 14, np.inf],
                               labels=["Same day", "1–3 days", "4–7 days", "8–14 days", "15+ days"])
a["booking_weekday"] = a.booking_date.dt.day_name()
a["appointment_weekday"] = a.appointment_date.dt.day_name()

def segment(col):
    return a.groupby(col, dropna=False, observed=False).agg(
        appointments=("appointment_id", "count"), no_shows=("no_show", "sum"),
        no_show_rate_pct=("no_show", lambda x: x.mean() * 100),
        avg_lead_time_days=("lead_time_days", "mean")
    ).reset_index().sort_values("no_show_rate_pct", ascending=False)

for col in ["specialty", "department", "patient_age_group", "insurance_type", "reason",
            "lead_time_cohort", "booking_hour", "appointment_weekday"]:
    segment(col).to_csv(REPORTS / f"deepdive_appointments_by_{col}.csv", index=False)

chi_rows = []
for col in ["specialty", "department", "patient_age_group", "insurance_type", "reason",
            "lead_time_cohort", "appointment_weekday"]:
    table = pd.crosstab(a[col], a.no_show)
    chi2, p, dof, expected = chi2_contingency(table)
    min_dim = min(table.shape[0] - 1, table.shape[1] - 1)
    cramer_v = np.sqrt(chi2 / (len(a) * min_dim)) if min_dim > 0 else np.nan
    chi_rows.append({"variable": col, "chi2": chi2, "degrees_freedom": dof,
                     "p_value": p, "cramers_v": cramer_v, "n": len(a)})
pd.DataFrame(chi_rows).to_csv(REPORTS / "deepdive_appointment_chi_square.csv", index=False)

# Exploratory logistic model: only information available before the appointment.
features = ["specialty", "department", "reason", "insurance_type", "patient_age_group",
            "booking_hour", "appointment_hour", "lead_time_days", "booking_weekday", "appointment_weekday"]
cat = ["specialty", "department", "reason", "insurance_type", "patient_age_group", "booking_weekday", "appointment_weekday"]
num = ["booking_hour", "appointment_hour", "lead_time_days"]
X, y = a[features], a.no_show.astype(int)
preprocess = ColumnTransformer([
    ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                      ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat),
    ("num", Pipeline([("impute", SimpleImputer(strategy="median")),
                      ("scale", StandardScaler())]), num)
])
model = Pipeline([("preprocess", preprocess),
                  ("classifier", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=42))])
baseline = DummyClassifier(strategy="most_frequent")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
baseline.fit(X_train, y_train)
model.fit(X_train, y_train)
pred, prob = model.predict(X_test), model.predict_proba(X_test)[:, 1]
metrics = {
    "model": "Balanced Logistic Regression", "target": "no_show",
    "features": features, "excluded_post_appointment_fields": ["wait_time_mins", "consultation_mins"],
    "train_rows": len(X_train), "test_rows": len(X_test),
    "accuracy": accuracy_score(y_test, pred), "precision": precision_score(y_test, pred, zero_division=0),
    "recall": recall_score(y_test, pred, zero_division=0), "f1": f1_score(y_test, pred, zero_division=0),
    "roc_auc": roc_auc_score(y_test, prob),
    "majority_class_baseline_accuracy": accuracy_score(y_test, baseline.predict(X_test)),
    "confusion_matrix": confusion_matrix(y_test, pred).tolist(),
    "note": "Exploratory single stratified 80/20 holdout; not approved for operational decisions."
}
(REPORTS / "appointment_logistic_regression_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
pd.DataFrame([{k:v for k,v in metrics.items() if k not in ["features","excluded_post_appointment_fields","confusion_matrix"]}]).to_csv(REPORTS / "appointment_model_metrics.csv", index=False)

summary = {
    "resource": {"records": len(r), "valid_bed_rows": int(r.bed_valid.sum()),
                 "valid_icu_rows": int(r.icu_valid.sum()), "mean_valid_bed_occupancy_pct": float(r.bed_occupancy_pct.mean()),
                 "mean_valid_icu_occupancy_pct": float(r.icu_occupancy_pct.mean()), "correlations": resource_corr},
    "satisfaction": {"records": len(s), "mean_overall_satisfaction": float(s.overall_satisfaction.mean()),
                     "correlations": sat_corr, "department_kruskal_wallis": {"statistic": float(kw.statistic), "p_value": float(kw.pvalue)}},
    "appointments": {"records": len(a), "no_show_count": int(a.no_show.sum()),
                     "no_show_rate_pct": float(a.no_show.mean()*100), "lead_time_min_days": int(a.lead_time_days.min()),
                     "lead_time_max_days": int(a.lead_time_days.max()), "chi_square_tests": chi_rows, "model": metrics}
}
(REPORTS / "deepdive_executive_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("Week 6 deep-dive analysis completed. See reports/deepdive_*.csv and JSON outputs.")
