from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"

st.set_page_config(page_title="Sunrise Healthcare Analytics", page_icon="🏥", layout="wide")

@st.cache_data
def load_data():
    r = pd.read_csv(RAW / "sunrise_resource_utilisation.csv", parse_dates=["date"])
    s = pd.read_csv(RAW / "sunrise_patient_satisfaction.csv", parse_dates=["survey_date"])
    a = pd.read_csv(RAW / "da_healthcare_appointments.csv", parse_dates=["booking_date", "appointment_date"])
    r["bed_valid"] = (r.occupied_beds <= r.total_beds) & (r.total_beds > 0)
    r["icu_valid"] = (r.icu_beds_occupied <= r.icu_beds_total) & (r.icu_beds_total > 0)
    r["surgery_valid"] = r.surgeries_completed <= r.surgeries_scheduled
    r["bed_occupancy_pct"] = (r.occupied_beds / r.total_beds * 100).where(r.bed_valid)
    r["icu_occupancy_pct"] = (r.icu_beds_occupied / r.icu_beds_total * 100).where(r.icu_valid)
    r["surgery_completion_pct"] = (r.surgeries_completed / r.surgeries_scheduled * 100).where(r.surgeries_scheduled > 0)
    s["feedback_comment"] = s["feedback_comment"].fillna("")
    a["no_show_label"] = a["no_show"].map({0:"Attended", 1:"No-show"})
    return r, s, a

r, s, a = load_data()
st.title("🏥 Sunrise Healthcare Analytics")
st.caption("Integrated analytics for hospital resources, patient experience and appointment operations")
st.info("Adapted project using the three supplied Sunrise datasets. This is healthcare operations analytics, not pharmaceutical SKU demand or expiry forecasting.")

with st.sidebar:
    st.header("Dashboard filters")
    hospitals = ["All"] + sorted(r.hospital.dropna().unique().tolist())
    selected_hospital = st.selectbox("Hospital (resource & satisfaction data)", hospitals)
    departments = ["All"] + sorted(r.department.dropna().unique().tolist())
    selected_department = st.selectbox("Department (resource data)", departments)
    st.divider()
    st.caption("Appointment data has no hospital identifier; it is analysed separately.")

rf = r.copy()
sf = s.copy()
if selected_hospital != "All":
    rf = rf[rf.hospital == selected_hospital]
    sf = sf[sf.hospital == selected_hospital]
if selected_department != "All":
    rf = rf[rf.department == selected_department]
    sf = sf[sf.department == selected_department]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Executive overview",
    "Resource utilisation",
    "Patient satisfaction",
    "Appointments",
    "Deep-dive insights"
])

with tab1:
    st.subheader("Executive overview")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Resource records", f"{len(rf):,}")
    c2.metric("Patient surveys", f"{len(sf):,}")
    c3.metric("Appointments", f"{len(a):,}")
    c4.metric("Appointment no-show rate", f"{a.no_show.mean()*100:.1f}%")
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Mean satisfaction", f"{sf.overall_satisfaction.mean():.2f}/5" if len(sf) else "N/A")
    c6.metric("Survey wait (mean)", f"{sf.waiting_time_mins.mean():.1f} min" if len(sf) else "N/A")
    c7.metric("Appointment wait (mean)", f"{a.wait_time_mins.mean():.1f} min")
    c8.metric("Resource wait (mean)", f"{rf.avg_patient_wait_mins.mean():.1f} min" if len(rf) else "N/A")
    st.markdown("### Key operational signals")
    k1,k2,k3 = st.columns(3)
    k1.warning(f"{int((~rf.bed_valid).sum())} resource rows have invalid bed capacity values in current filter.")
    k2.warning(f"{int((~rf.icu_valid).sum())} resource rows have invalid ICU capacity values in current filter.")
    k3.warning(f"{int((~rf.surgery_valid).sum())} resource rows report more surgeries completed than scheduled.")
    st.markdown("### Dataset coverage")
    coverage = pd.DataFrame({
        "Dataset":["Resource utilisation","Patient satisfaction","Appointments"],
        "Records":[len(r),len(s),len(a)],
        "Start":[r.date.min().date(),s.survey_date.min().date(),a.appointment_date.min().date()],
        "End":[r.date.max().date(),s.survey_date.max().date(),a.appointment_date.max().date()]
    })
    st.dataframe(coverage, use_container_width=True, hide_index=True)
    st.caption("The three datasets cover different periods and have different grains; do not join them row-by-row.")

with tab2:
    st.subheader("Hospital resource utilisation")
    valid_beds = rf[rf.bed_valid]
    valid_icu = rf[rf.icu_valid]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Valid bed records", f"{len(valid_beds):,}/{len(rf):,}")
    m2.metric("Mean bed occupancy (valid only)", f"{valid_beds.bed_occupancy_pct.mean():.1f}%" if len(valid_beds) else "N/A")
    m3.metric("Mean ICU occupancy (valid only)", f"{valid_icu.icu_occupancy_pct.mean():.1f}%" if len(valid_icu) else "N/A")
    m4.metric("Mean doctor attendance", f"{rf.doctor_attendance_pct.mean():.1f}%" if len(rf) else "N/A")
    if len(valid_beds):
        by_h = valid_beds.groupby("hospital",as_index=False).bed_occupancy_pct.mean()
        st.plotly_chart(px.bar(by_h,x="hospital",y="bed_occupancy_pct",title="Average bed occupancy by hospital (valid records only)",labels={"bed_occupancy_pct":"Occupancy (%)","hospital":"Hospital"}),use_container_width=True)
    monthly = rf.dropna(subset=["date"]).assign(month=lambda d:d.date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(wait_mins=("avg_patient_wait_mins","mean"),doctor_attendance=("doctor_attendance_pct","mean"),nurse_attendance=("nurse_attendance_pct","mean"))
    st.plotly_chart(px.line(monthly,x="month",y=["wait_mins"],title="Average resource-record waiting time over time",labels={"value":"Minutes","month":"Month"}),use_container_width=True)
    st.plotly_chart(px.bar(rf.groupby("department",as_index=False).agg(records=("record_id","count"),wait=("avg_patient_wait_mins","mean")).sort_values("wait",ascending=False),x="department",y="wait",title="Average waiting time by department",labels={"wait":"Minutes","department":"Department"}),use_container_width=True)
    st.caption("Invalid capacity records are excluded from occupancy-rate calculations, but retained in raw data and counted in quality warnings.")

with tab3:
    st.subheader("Patient satisfaction")
    if len(sf):
        x1,x2,x3 = st.columns(3)
        x1.metric("Overall satisfaction",f"{sf.overall_satisfaction.mean():.2f}/5")
        x2.metric("Would recommend — Yes",f"{(sf.would_recommend=='Yes').mean()*100:.1f}%")
        x3.metric("Average reported wait",f"{sf.waiting_time_mins.mean():.1f} min")
        ratings = sf[["doctor_rating","nurse_rating","cleanliness_rating","billing_clarity_rating","overall_satisfaction"]].mean().rename_axis("dimension").reset_index(name="average_rating")
        st.plotly_chart(px.bar(ratings,x="dimension",y="average_rating",title="Average patient ratings by dimension",labels={"dimension":"Rating dimension","average_rating":"Average rating (1–5)"}),use_container_width=True)
        rec = sf.would_recommend.value_counts().rename_axis("response").reset_index(name="count")
        st.plotly_chart(px.pie(rec,names="response",values="count",title="Would patients recommend the hospital?"),use_container_width=True)
        dept = sf.groupby("department",as_index=False).agg(satisfaction=("overall_satisfaction","mean"),surveys=("survey_id","count"),wait=("waiting_time_mins","mean")).sort_values("satisfaction")
        st.plotly_chart(px.bar(dept,x="department",y="satisfaction",title="Average satisfaction by department",hover_data=["surveys","wait"],labels={"satisfaction":"Average satisfaction (1–5)"}),use_container_width=True)
        comments = sf[sf.feedback_comment.str.strip()!=""][["survey_date","department","overall_satisfaction","feedback_comment"]].sort_values("survey_date",ascending=False)
        st.markdown("#### Recent written feedback")
        st.dataframe(comments.head(30),use_container_width=True,hide_index=True)
    else:
        st.warning("No survey records match the selected filters.")

with tab4:
    st.subheader("Appointment operations")
    q1,q2,q3,q4 = st.columns(4)
    q1.metric("Appointments",f"{len(a):,}")
    q2.metric("No-shows",f"{int(a.no_show.sum()):,}")
    q3.metric("No-show rate",f"{a.no_show.mean()*100:.1f}%")
    q4.metric("Average wait",f"{a.wait_time_mins.mean():.1f} min")
    month = a.assign(month=a.appointment_date.dt.to_period("M").astype(str)).groupby("month",as_index=False).agg(appointments=("appointment_id","count"),no_show_rate=("no_show","mean"))
    st.plotly_chart(px.line(month,x="month",y="appointments",title="Appointment volume by appointment month"),use_container_width=True)
    specialty = a.groupby("specialty",as_index=False).agg(appointments=("appointment_id","count"),no_show_rate=("no_show","mean"),avg_wait=("wait_time_mins","mean")).sort_values("appointments",ascending=False)
    st.plotly_chart(px.bar(specialty,x="specialty",y="appointments",title="Appointment volume by specialty",hover_data=["no_show_rate","avg_wait"]),use_container_width=True)
    st.plotly_chart(px.bar(specialty.sort_values("no_show_rate",ascending=False),x="specialty",y="no_show_rate",title="No-show rate by specialty",labels={"no_show_rate":"No-show rate"}),use_container_width=True)
    st.markdown("#### Appointment data")
    st.dataframe(a.head(100),use_container_width=True,hide_index=True)


with tab5:
    st.subheader("Deep-dive Insights")
    st.caption(
        "Explore hospital performance, patient satisfaction "
        "and appointment attendance patterns."
    )

    # Satisfaction by department
    st.markdown("### Patient satisfaction by department")

    satisfaction_dept = sf.groupby(
        "department", as_index=False
    ).agg(
        mean_satisfaction=("overall_satisfaction", "mean"),
        survey_count=("survey_id", "count"),
        mean_wait=("waiting_time_mins", "mean")
    ).sort_values("mean_satisfaction")

    st.plotly_chart(
        px.bar(
            satisfaction_dept,
            x="department",
            y="mean_satisfaction",
            hover_data=["survey_count", "mean_wait"],
            title="Average Satisfaction by Department",
            labels={
                "mean_satisfaction": "Satisfaction (out of 5)"
            }
        ),
        use_container_width=True
    )

    # Appointment no-show segmentation
    st.markdown("### Appointment no-show analysis")

    specialty_analysis = a.groupby(
        "specialty", as_index=False
    ).agg(
        appointments=("appointment_id", "count"),
        no_show_rate=("no_show", "mean")
    ).sort_values("no_show_rate", ascending=False)

    st.plotly_chart(
        px.bar(
            specialty_analysis,
            x="specialty",
            y="no_show_rate",
            hover_data=["appointments"],
            title="No-show Rate by Specialty",
            labels={"no_show_rate": "No-show rate"}
        ),
        use_container_width=True
    )

    # Resource waiting time
    st.markdown("### Resource performance by department")

    resource_analysis = rf.groupby(
        "department", as_index=False
    ).agg(
        mean_wait=("avg_patient_wait_mins", "mean"),
        doctor_attendance=("doctor_attendance_pct", "mean"),
        nurse_attendance=("nurse_attendance_pct", "mean")
    ).sort_values("mean_wait", ascending=False)

    st.plotly_chart(
        px.bar(
            resource_analysis,
            x="department",
            y="mean_wait",
            hover_data=[
                "doctor_attendance",
                "nurse_attendance"
            ],
            title="Average Waiting Time by Department"
        ),
        use_container_width=True
    )

    # KPI definitions
    st.markdown("### KPI definitions")

    definitions = pd.DataFrame([
        ["Bed occupancy", "Occupied beds / Total beds × 100"],
        ["ICU occupancy", "Occupied ICU beds / Total ICU beds × 100"],
        ["No-show rate", "No-show appointments / Total appointments × 100"],
        ["Patient satisfaction", "Mean overall satisfaction rating"],
        ["Average waiting time", "Mean recorded waiting time"]
    ], columns=["KPI", "Calculation"])

    st.dataframe(
        definitions,
        use_container_width=True,
        hide_index=True
    )


st.divider()
st.caption("Prepared for the adapted PharmaLink internship project | Source: supplied Sunrise CSV datasets | Analysis is descriptive and does not establish causation.")
