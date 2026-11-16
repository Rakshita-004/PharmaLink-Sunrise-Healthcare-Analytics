# SUNRISE HEALTHCARE ANALYTICS
## Final Strategic Brief – Week 12

**Prepared for:** Sunrise Healthcare Management  
**Project:** PharmaLink Adapted Healthcare Analytics  
**Evidence base:** 400 resource records, 600 patient surveys and 2,000 appointment records.

### 1. Situation

Sunrise Healthcare requires better visibility into hospital resource utilization, patient experience and appointment attendance. The supplied datasets provide operational information across these three areas.

The analysis identifies opportunities to improve data reliability, appointment management and patient flow. However, the datasets have different time periods and levels of detail, and the appointment dataset does not contain a hospital identifier.

This project is an adapted healthcare operations analytics solution. The supplied datasets do not contain pharmaceutical SKU sales, inventory, batch or expiry information.

### 2. Key Findings

**Resource Utilization**

- 400 resource records across four hospitals and nine departments.
- Average resource waiting time: 78.66 minutes.
- Valid bed occupancy average: 54.08%.
- Valid ICU occupancy average: 52.52%.
- 175 invalid bed-capacity records.
- 175 invalid ICU-capacity records.
- 182 inconsistent surgery-count records.
- Radiology has the highest departmental average resource waiting time at 87.88 minutes.

**Patient Satisfaction**

- 600 patient survey records.
- Average satisfaction: 3.045/5.
- Average reported survey waiting time: 91.43 minutes.
- Emergency has the lowest departmental satisfaction average at 2.85/5.
- Surgery has the highest departmental satisfaction average at 3.27/5.

Department-level satisfaction differences were not statistically significant (Kruskal–Wallis p = 0.803).

**Appointment Analytics**

- 2,000 appointment records.
- 324 no-show appointments.
- Overall no-show rate: 16.2%.
- General Medicine: 22.50%.
- Dermatology: 20.46%.
- Ophthalmology: 19.93%.

Specialty was significantly associated with appointment no-show status (chi-square p = 0.000031).

The exploratory logistic regression model achieved a ROC-AUC of 0.566 and is not suitable for operational deployment without further validation.

### 3. Business Implications

The analysis highlights three important management considerations.

First, inaccurate resource records can undermine hospital capacity planning. Second, appointment attendance varies across specialties, creating opportunities for targeted interventions. Third, waiting-time patterns indicate areas where operational investigation may improve patient experience.

Management should use the dashboard as a decision-support tool while continuing to validate the underlying operational data.

### 4. Three Prioritized Recommendations

**Priority 1: Improve Data Quality and Reliability**

Introduce validation rules for bed capacity, ICU capacity and surgery counts. Assign responsibility for correcting invalid records and establish regular data-quality reporting.

**Proposed 90-day target:** Achieve at least 99% valid capacity and surgery records in subsequent reporting extracts.

**Expected impact:** More reliable KPIs, improved capacity planning and fewer misleading operational alerts.

**Priority 2: Reduce Appointment No-Shows**

Focus on General Medicine, Dermatology and Ophthalmology, which have the highest observed no-show rates. Pilot appointment confirmation messages, reminders and simpler cancellation or rescheduling options.

**Proposed target:** Reduce the overall no-show rate by 10% relative to the 16.2% baseline, reaching approximately 14.6%.

At comparable appointment volume, this would mean approximately 32 fewer no-shows per 2,000 appointments.

**Expected impact:** Better appointment-slot utilization and fewer unused consultation opportunities.

**Priority 3: Improve Waiting Times and Patient Experience**

Investigate patient-flow bottlenecks in Radiology and review patient experience in Emergency and other lower-scoring areas. Examine scheduling, queue communication and escalation processes.

**Proposed target:** Pilot a 10% reduction in Radiology's 87.88-minute average resource waiting time.

**Expected impact:** Shorter waiting times, improved service efficiency and a more measurable patient-experience improvement process.

### 5. Measurement Plan

Monitor the following indicators monthly:

- Valid bed and ICU capacity records.
- Invalid surgery-count records.
- Department-level waiting times.
- Overall patient satisfaction.
- Appointment no-show rates by specialty.
- Appointment volumes and cancellations.

Compare results across equivalent reporting periods and document any operational changes.

### 6. Assumptions and Limitations

The findings are descriptive and exploratory rather than causal. The three datasets have different grains and coverage and have not been joined row-by-row.

Invalid resource records are excluded from relevant occupancy calculations. Invalid data flags may overlap. The appointment dataset has no hospital identifier.

The predictive model requires further development and validation before operational use. Proposed improvement targets must be reviewed with operational stakeholders.

### 7. Final Strategic Conclusion

Sunrise Healthcare should prioritize source-data reliability, targeted appointment attendance interventions and waiting-time improvement initiatives.

The completed analytics dashboard provides management with an integrated view of operational performance, patient satisfaction and appointment attendance.

The recommended actions establish a measurable foundation for continuous improvement and evidence-based healthcare management.