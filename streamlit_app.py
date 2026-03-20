import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="NOH JHB Maternity Outcomes", layout="wide")

st.title("NOH Johannesburg Maternity Outcomes")
st.caption("De identified monthly outcomes reported by baby date of birth")

@st.cache_data
def load_data():
    df = pd.read_csv("data/jhb_outcomes_monthly.csv")
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_data()

tab_dash, tab_narr = st.tabs(["Dashboard", "Narrative"])

min_date = df["month"].min().date()
max_date = df["month"].max().date()

with tab_dash:
    start, end = st.date_input(
        "Select reporting period",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    f = df[(df["month"] >= start) & (df["month"] <= end)].copy()
    f = f.sort_values("month").copy()

    # Intended mode of delivery metrics
    f["intended_vaginal_den"] = (f["births_total"] - f["elective_cs_count"]).clip(lower=0)

    f["intrapartum_cs_rate"] = (
        f["emergency_cs_count"] / f["intended_vaginal_den"].replace(0, pd.NA)
    )

    f["vaginal_success_rate"] = (
        f["nvd_count"] / f["intended_vaginal_den"].replace(0, pd.NA)
    )

    f["elective_share"] = (
        f["elective_cs_count"] / f["births_total"].replace(0, pd.NA)
    )

    # System level rates for truth display
    f["cs_rate_total"] = (
        (f["elective_cs_count"] + f["emergency_cs_count"])
        / f["births_total"].replace(0, pd.NA)
    )

    f["nicu_rate_total"] = (
        f["nicu_admissions_total"]
        / f["births_total"].replace(0, pd.NA)
    )

    # Rolling averages for interpretation only
    f["cs_rate_roll3"] = f["cs_rate_total"].rolling(3, min_periods=1).mean()
    f["nicu_rate_roll3"] = f["nicu_rate_total"].rolling(3, min_periods=1).mean()

    markers = pd.DataFrame(
        {
            "month": pd.to_datetime(["2023-07-01", "2024-03-01", "2025-12-01"]),
            "label": [
                "Workforce transition phase",
                "Sustained CS elevation begins",
                "Ward staffing shock noted",
            ],
        }
    )

    st.subheader("How to read this dashboard")
    st.write("Monthly values are shown as the primary series")
    st.write("Three month rolling averages are shown for interpretation and annotation only")
    st.write("Markers highlight system change points used in the narrative")

    st.divider()
    st.subheader("System level trends")

    left, right = st.columns(2)

    base_cs_monthly = alt.Chart(f).mark_line(point=True).encode(
        x=alt.X("month:T", title="Baby DOB Period"),
        y=alt.Y("cs_rate_total:Q", title="CS rate", axis=alt.Axis(format="%")),
        tooltip=[
            "month:T",
            alt.Tooltip("births_total:Q", title="Births"),
            alt.Tooltip("elective_cs_count:Q", title="Elective CS"),
            alt.Tooltip("emergency_cs_count:Q", title="Emergency CS"),
            alt.Tooltip("cs_rate_total:Q", title="CS rate", format=".1%"),
        ],
    )

    cs_roll = alt.Chart(f).mark_line(strokeDash=[6, 4]).encode(
        x="month:T",
        y=alt.Y("cs_rate_roll3:Q", axis=alt.Axis(format="%")),
        tooltip=[
            "month:T",
            alt.Tooltip("cs_rate_roll3:Q", title="CS roll3", format=".1%"),
        ],
    )

    base_nicu_monthly = alt.Chart(f).mark_line(point=True).encode(
        x=alt.X("month:T", title="Baby DOB Period"),
        y=alt.Y("nicu_rate_total:Q", title="NICU rate", axis=alt.Axis(format="%")),
        tooltip=[
            "month:T",
            alt.Tooltip("births_total:Q", title="Births"),
            alt.Tooltip("nicu_admissions_total:Q", title="NICU total"),
            alt.Tooltip("nicu_admissions_term:Q", title="NICU term"),
            alt.Tooltip("nicu_rate_total:Q", title="NICU rate", format=".1%"),
        ],
    )

    nicu_roll = alt.Chart(f).mark_line(strokeDash=[6, 4]).encode(
        x="month:T",
        y=alt.Y("nicu_rate_roll3:Q", axis=alt.Axis(format="%")),
        tooltip=[
            "month:T",
            alt.Tooltip("nicu_rate_roll3:Q", title="NICU roll3", format=".1%"),
        ],
    )

    marker_rules = alt.Chart(markers).mark_rule(opacity=0.6).encode(x="month:T")
    marker_text = alt.Chart(markers).mark_text(align="left", baseline="top", dx=6, dy=6).encode(
        x="month:T", text="label:N"
    )

    cs_chart = alt.layer(base_cs_monthly, cs_roll, marker_rules, marker_text).properties(height=320)
    nicu_chart = alt.layer(base_nicu_monthly, nicu_roll, marker_rules, marker_text).properties(height=320)

    left.altair_chart(cs_chart, use_container_width=True)
    right.altair_chart(nicu_chart, use_container_width=True)

    st.caption("Solid line shows monthly values")
    st.caption("Dashed line shows three month rolling average for interpretation and annotation only")

    st.divider()

    births = int(f["births_total"].sum())
    elcs_total = int(f["elective_cs_count"].sum())
    emcs_total = int(f["emergency_cs_count"].sum())
    nvd_total = int(f["nvd_count"].sum())

    intended_vaginal_total = int((f["births_total"] - f["elective_cs_count"]).sum())

    intrapartum_cs_rate_total = emcs_total / max(1, intended_vaginal_total)
    vaginal_success_rate_total = nvd_total / max(1, intended_vaginal_total)
    elective_share_total = elcs_total / max(1, births)

    nicu_total = int(f["nicu_admissions_total"].sum())
    nicu_rate_total = nicu_total / max(1, births)

    st.subheader("Headline outcomes for intended vaginal births")

    k1, k2, k3 = st.columns(3)
    k4, k5, k6 = st.columns(3)

    k1.metric("Births", births)
    k2.metric("Elective CS share", f"{elective_share_total:.1%}")
    k3.metric("Intended vaginal births", intended_vaginal_total)
    k4.metric("Intrapartum CS rate", f"{intrapartum_cs_rate_total:.1%}")
    k5.metric("Vaginal success rate", f"{vaginal_success_rate_total:.1%}")
    k6.metric("NICU rate", f"{nicu_rate_total:.1%}")

    st.caption("Elective caesareans are treated as planned surgical births and removed from the denominator")
    st.caption("Intended vaginal births equal total births minus elective caesareans")
    st.caption("Intrapartum caesarean rate reflects conversion from planned vaginal birth to emergency surgery")

    st.divider()
    st.subheader("Intended vaginal pathway performance over time")

    c1, c2 = st.columns(2)

    intra_chart = alt.Chart(f).mark_line(point=True).encode(
        x=alt.X("month:T", title="Baby DOB Period"),
        y=alt.Y("intrapartum_cs_rate:Q", title="Intrapartum CS rate", axis=alt.Axis(format="%")),
        tooltip=[
            "month:T",
            alt.Tooltip("intrapartum_cs_rate:Q", format=".1%"),
            alt.Tooltip("intended_vaginal_den:Q", title="Intended vaginal births"),
            alt.Tooltip("emergency_cs_count:Q", title="Emergency CS"),
            alt.Tooltip("births_total:Q", title="Births"),
        ],
    ).properties(height=320)

    success_chart = alt.Chart(f).mark_line(point=True).encode(
        x=alt.X("month:T", title="Baby DOB Period"),
        y=alt.Y("vaginal_success_rate:Q", title="Vaginal success rate", axis=alt.Axis(format="%")),
        tooltip=[
            "month:T",
            alt.Tooltip("vaginal_success_rate:Q", format=".1%"),
            alt.Tooltip("intended_vaginal_den:Q", title="Intended vaginal births"),
            alt.Tooltip("nvd_count:Q", title="NVD"),
            alt.Tooltip("births_total:Q", title="Births"),
        ],
    ).properties(height=320)

    c1.altair_chart(intra_chart, use_container_width=True)
    c2.altair_chart(success_chart, use_container_width=True)

    st.subheader("Monthly intended vaginal metrics")
    t = f[
        [
            "month",
            "births_total",
            "elective_cs_count",
            "intended_vaginal_den",
            "nvd_count",
            "emergency_cs_count",
            "intrapartum_cs_rate",
            "vaginal_success_rate",
            "nicu_admissions_total",
            "nicu_admissions_term",
        ]
    ].copy()
    t["month"] = t["month"].dt.strftime("%Y-%m")
    st.dataframe(t, use_container_width=True)

with tab_narr:
    st.subheader("NOH JHB Maternity Outcomes Narrative")
    st.write("This narrative is the source of truth for interpreting the dashboard.")
    st.write("It aligns exactly with the metrics and denominators used in the dashboard.")
    st.write("Refer to the locked narrative document for the full audit grade text.")
