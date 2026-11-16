from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
OUT.mkdir(parents=True, exist_ok=True)

resource = pd.read_csv(RAW / "sunrise_resource_utilisation.csv")
satisfaction = pd.read_csv(RAW / "sunrise_patient_satisfaction.csv")
appointments = pd.read_csv(RAW / "da_healthcare_appointments.csv")

# Parse dates without silently discarding invalid values.
resource["date"] = pd.to_datetime(resource["date"], errors="coerce")
satisfaction["survey_date"] = pd.to_datetime(satisfaction["survey_date"], errors="coerce")
appointments["booking_date"] = pd.to_datetime(appointments["booking_date"], errors="coerce")
appointments["appointment_date"] = pd.to_datetime(appointments["appointment_date"], errors="coerce")

# Preserve original measurements and add explicit quality flags.
resource["flag_bed_capacity_invalid"] = resource["occupied_beds"] > resource["total_beds"]
resource["flag_icu_capacity_invalid"] = resource["icu_beds_occupied"] > resource["icu_beds_total"]
resource["flag_surgery_count_invalid"] = resource["surgeries_completed"] > resource["surgeries_scheduled"]
resource["flag_any_resource_issue"] = resource[
    ["flag_bed_capacity_invalid", "flag_icu_capacity_invalid", "flag_surgery_count_invalid"]
].any(axis=1)

# Derived metrics are calculated only where their denominators are meaningful.
resource["bed_occupancy_pct"] = (
    resource["occupied_beds"] / resource["total_beds"].where(resource["total_beds"] > 0) * 100
)
resource["icu_occupancy_pct"] = (
    resource["icu_beds_occupied"] / resource["icu_beds_total"].where(resource["icu_beds_total"] > 0) * 100
)
resource["surgery_completion_pct"] = (
    resource["surgeries_completed"] / resource["surgeries_scheduled"].where(resource["surgeries_scheduled"] > 0) * 100
)

# Keep optional free-text feedback missing; do not invent comments.
satisfaction["feedback_comment"] = satisfaction["feedback_comment"].fillna("")

# A zero consultation duration aligns with no-show rows in this file; retain and flag.
appointments["flag_zero_consultation"] = appointments["consultation_mins"] == 0
appointments["flag_zero_consultation_attended"] = (
    appointments["flag_zero_consultation"] & (appointments["no_show"] == 0)
)

resource.to_csv(OUT / "resource_utilisation_audited.csv", index=False)
satisfaction.to_csv(OUT / "patient_satisfaction_prepared.csv", index=False)
appointments.to_csv(OUT / "appointments_prepared.csv", index=False)

summary = [
    ("resource_rows", len(resource)),
    ("satisfaction_rows", len(satisfaction)),
    ("appointment_rows", len(appointments)),
    ("resource_invalid_bed_capacity", int(resource["flag_bed_capacity_invalid"].sum())),
    ("resource_invalid_icu_capacity", int(resource["flag_icu_capacity_invalid"].sum())),
    ("resource_invalid_surgery_counts", int(resource["flag_surgery_count_invalid"].sum())),
    ("appointment_no_show_rate_pct", round(appointments["no_show"].mean() * 100, 2)),
    ("satisfaction_missing_feedback_comments", int((satisfaction["feedback_comment"] == "").sum())),
]
pd.DataFrame(summary, columns=["metric", "value"]).to_csv(REPORTS / "initial_audit_summary.csv", index=False)
print("Audit complete. Review reports/initial_audit_summary.csv and data/processed/.")
