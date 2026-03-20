NOH Johannesburg Clinical Outcomes Dashboard

This repository contains the Streamlit dashboard and narrative used to present
monthly maternity outcomes for the Network One Health (NOH) Johannesburg centre
at Busamed Modderfontein.

The dashboard is designed for clinical governance, funder engagement, and
programme improvement. It provides transparent visibility of outcomes without
smoothing, selective exclusion, or performance marketing.

Scope
- Single centre: NOH Johannesburg (Busamed Modderfontein)
- Reporting unit: Monthly, baby date of birth
- Period covered: June 2022 to March 2026
- Data type: De-identified, aggregated clinical outcomes

What the dashboard shows
- System-level trends in caesarean section (CS) and NICU admission rates
- Three-month rolling averages used for interpretation only
- Explicit markers for system transition and operational stress periods
- Intended vaginal pathway metrics, separating planned surgical births
  from intrapartum conversion

Key interpretation principles
- Elective caesarean sections are treated as planned surgical births and
  removed from the denominator when assessing intrapartum performance
- Emergency caesarean section is treated as a quality-sensitive indicator
- NICU outcomes are interpreted alongside delivery mode rather than in isolation
- Low-volume months are retained to preserve visibility of system stress

Narrative alignment
The dashboard narrative is locked and governed by a clinical outcomes narrative
document. All captions, markers, and interpretations in the app are aligned
verbatim to that source of truth.

See:
docs/NOH_JHB_Maternity_Outcomes_Narrative.md

Repository structure
- streamlit_app.py          Streamlit application
- data/                     De-identified monthly outcomes dataset
- docs/                     Locked narrative and governance documents
- requirements.txt          Python dependencies

Running the app locally
pip install -r requirements.txt
streamlit run streamlit_app.py

Deployment
This app is designed to be deployed via Streamlit Cloud using the main branch
and streamlit_app.py as the entry point.

Governance note
This dashboard is an active governance tool. It is used to support audit,
learning, and improvement discussions and does not make causal claims or
individual clinician attribution.
