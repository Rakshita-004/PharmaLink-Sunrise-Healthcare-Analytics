"""
Repeatable ETL pipeline for Sunrise Healthcare Analytics.
Run from project root:
    python src/data_pipeline.py
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
PROCESSED.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

def load_csv(filename, date_columns):
    path = RAW / filename
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    df = pd.read_csv(path)
    for col in date_columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def main():
    resource = load_csv("sunrise_resource_utilisation.csv", ["date"])
    satisfaction = load_csv("sunrise_patient_satisfaction.csv", ["survey_date"])
    appointments = load_csv(
        "da_healthcare_appointments.csv", ["booking_date", "appointment_date"]
    )

    # Data-quality flags preserve source values and make invalid records visible.
    resource["flag_bed_capacity_invalid"] = (
        (resource["total_beds"] <= 0) |
        (resource["occupied_beds"] < 0) |
        (resource["occupied_beds"] > resource["total_beds"])
    )
    resource["flag_icu_capacity_invalid"] = (
        (resource["icu_beds_total"] <= 0) |
        (resource["icu_beds_occupied"] < 0) |
        (resource["icu_beds_occupied"] > resource["icu_beds_total"])
    )
    resource["flag_surgery_count_invalid"] = (
        (resource["surgeries_scheduled"] < 0) |
        (resource["surgeries_completed"] < 0) |
        (resource["surgeries_completed"] > resource["surgeries_scheduled"])
    )

    # Derived percentages are only calculated where the source values are valid.
    resource["bed_occupancy_pct"] = (
        resource["occupied_beds"] / resource["total_beds"] * 100
    ).where(~resource["flag_bed_capacity_invalid"])
    resource["icu_occupancy_pct"] = (
        resource["icu_beds_occupied"] / resource["icu_beds_total"] * 100
    ).where(~resource["flag_icu_capacity_invalid"])
    resource["surgery_completion_pct"] = (
        resource["surgeries_completed"] / resource["surgeries_scheduled"] * 100
    ).where(
        (resource["surgeries_scheduled"] > 0) &
        (~resource["flag_surgery_count_invalid"])
    )

    # Feedback comments are optional text; preserve missingness as empty text for display.
    satisfaction["feedback_comment"] = satisfaction["feedback_comment"].fillna("")
    satisfaction["flag_feedback_missing"] = satisfaction["feedback_comment"].str.strip().eq("")

    # Appointment data has no hospital ID; do not fabricate one.
    appointments["no_show_label"] = appointments["no_show"].map({0: "Attended", 1: "No-show"})
    appointments["flag_zero_consultation"] = appointments["consultation_mins"].eq(0)

    # Save reproducible prepared outputs.
    resource.to_csv(PROCESSED / "resource_utilisation_processed.csv", index=False)
    satisfaction.to_csv(PROCESSED / "patient_satisfaction_processed.csv", index=False)
    appointments.to_csv(PROCESSED / "appointments_processed.csv", index=False)

    # Baseline KPI definitions are descriptive, not predictive model scores.
    kpis = [
        ("Resource records", len(resource), "records", "All resource records"),
        ("Mean doctor attendance", round(resource["doctor_attendance_pct"].mean(), 2), "%", "Mean across resource records"),
        ("Mean nurse attendance", round(resource["nurse_attendance_pct"].mean(), 2), "%", "Mean across resource records"),
        ("Mean resource waiting time", round(resource["avg_patient_wait_mins"].mean(), 2), "minutes", "Mean across resource records"),
        ("Invalid bed-capacity records", int(resource["flag_bed_capacity_invalid"].sum()), "records", "Occupied beds > total beds or invalid denominator"),
        ("Invalid ICU-capacity records", int(resource["flag_icu_capacity_invalid"].sum()), "records", "Occupied ICU beds > total ICU beds or invalid denominator"),
        ("Invalid surgery-count records", int(resource["flag_surgery_count_invalid"].sum()), "records", "Completed surgeries > scheduled surgeries or negative counts"),
        ("Patient survey records", len(satisfaction), "records", "All survey records"),
        ("Mean overall satisfaction", round(satisfaction["overall_satisfaction"].mean(), 3), "out of 5", "Mean survey rating"),
        ("Mean survey waiting time", round(satisfaction["waiting_time_mins"].mean(), 2), "minutes", "Mean reported survey wait"),
        ("Missing feedback comments", int(satisfaction["flag_feedback_missing"].sum()), "comments", "Optional free-text feedback blank"),
        ("Appointment records", len(appointments), "records", "All appointment records"),
        ("Appointment no-shows", int(appointments["no_show"].sum()), "records", "no_show = 1"),
        ("Appointment no-show rate", round(appointments["no_show"].mean() * 100, 2), "%", "No-shows / all appointment records"),
        ("Mean appointment waiting time", round(appointments["wait_time_mins"].mean(), 2), "minutes", "Mean recorded appointment wait"),
        ("Mean attended consultation duration", round(appointments.loc[appointments["no_show"] == 0, "consultation_mins"].mean(), 2), "minutes", "Mean consultation duration among attended appointments"),
    ]
    kpi_df = pd.DataFrame(kpis, columns=["metric", "value", "unit", "definition"])
    kpi_df.to_csv(REPORTS / "baseline_metrics.csv", index=False)

    quality = {
        "resource_rows": len(resource),
        "satisfaction_rows": len(satisfaction),
        "appointment_rows": len(appointments),
        "resource_duplicate_rows": int(resource.duplicated().sum()),
        "satisfaction_duplicate_rows": int(satisfaction.duplicated().sum()),
        "appointment_duplicate_rows": int(appointments.duplicated().sum()),
        "resource_invalid_bed_capacity": int(resource["flag_bed_capacity_invalid"].sum()),
        "resource_invalid_icu_capacity": int(resource["flag_icu_capacity_invalid"].sum()),
        "resource_invalid_surgery_counts": int(resource["flag_surgery_count_invalid"].sum()),
        "satisfaction_missing_feedback_comments": int(satisfaction["flag_feedback_missing"].sum()),
        "appointment_missing_values": int(appointments.isna().sum().sum()),
        "appointment_hospital_identifier_available": False
    }
    (REPORTS / "pipeline_quality_summary.json").write_text(
        json.dumps(quality, indent=2), encoding="utf-8"
    )
    print("Pipeline completed successfully.")
    print(f"Processed files: {PROCESSED}")
    print(f"Baseline metrics: {REPORTS / 'baseline_metrics.csv'}")
    print(f"Quality summary: {REPORTS / 'pipeline_quality_summary.json'}")

if __name__ == "__main__":
    main()
