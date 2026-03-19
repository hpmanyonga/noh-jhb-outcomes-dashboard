import pandas as pd
import streamlit as st
import altair as alt

st.set_page_config(
    page_title="NOH JHB Outcomes (De-identified)",
    layout="wide"
)

st.title("NOH JHB — Outcomes Dashboard (De-identified)")
st.caption("Aggregated counts only. No client or provider personal data displayed.")

@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/jhb_outcomes_monthly.csv",
        sep=",",
        engine="python",
        encoding="utf-8-sig",
        on_bad_lines="skip"
    )
    expected_cols = [
    "month",
    "births_total",
    "nvd_count",
    "elective_cs_count

    df = df[expected_cols]

    df["month"] = pd.to_datetime(df["month"], errors="coerce")
    df = df.dropna(subset=["month"])
    df = df.sort_values("month")

    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Data load error: {e}")
    st.stop()

min_m = df["month"].min()
max_m = df["month"].max()

st.caption(f"Coverage: {min_m:%Y-%m} to {max_m:%Y-%m} (Baby DOB Period)")

start, end = st.sidebar.slider(
    "Baby DOB Period (headline)",
    min_value=min_m.to_pydatetime(),
    max_value=max_m.to_pydatetime(),
    value=(min_m.to_pydatetime(), max_m.to_pydatetime())
)

f = df[(df["month"] >= start) & (df["month"] <= end)].copy()
# Intended mode of delivery metrics
f["intended_vaginal_den"] = (f["births_total"] - f["elective_cs_count"]).clip(lower=0)

f["intrapartum_cs_rate"] = (
    f["emergency_cs_count"] / f["intended_vaginal_den"].replace(0, pd.NA)
)

f["vaginal_success_rate"] = (
    f["nvd_count"] / f["intended_vaginal_den"].replace(0, pd.NA
births = int(f["births_total"].sum())
cs_total = int((f["elective_cs_count"] + f["emergency_cs_count"]).sum())
emcs_total = int(f["emergency_cs_count"].sum())

cs_rate = cs_total / max(1, births)
emcs_rate = emcs_total / max(1, births)

# Headline totals for selected period
births = int(f["births_total"].sum())
elcs_total = int(f["elective_cs_count"].sum())
emcs_total = int(f["emergency_cs_count"].sum())
nvd_total = int(f["nvd_count"].sum())

intended_vaginal_total = int((f["births_total"] - f["elective_cs_count"]).sum())

intrapartum_cs_rate_total = (
    emcs_total / max(1, intended_vaginal_total)
)

vaginal_success_rate_total = (
    nvd_total / max(1, intended_vaginal_total)
)

elective_share_total = (
    elcs_total / max(1, births)
)

nicu_total = int(f["nicu_admissions_total"].sum())
nicu_term_total = int(f["nicu_admissions_term"].sum())
nicu_rate_total = nicu_total / max(1, births)

st.subheader("Headline outcomes for intended vaginal births")
k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Births", f"{births}")
k2.metric("Elective CS share", f"{elective_share_total:.1%}")
k3.metric("Intended vaginal births", f"{intended_vaginal_total}")
k4.metric("Intrapartum CS rate", f"{intrapartum_cs_rate_total:.1%}")
k5.metric("Vaginal success rate", f"{vaginal_success_rate_total:.1%}")
k6.metric("NICU rate", f"{nicu_rate_total:.1%}")
st.divider()

st.subheader("Intended vaginal pathway performance over time")

cA, cB = st.columns(2)

intra_chart = alt.Chart(f).mark_line(point=True).encode(
    x=alt.X("month:T", title="Baby DOB Period"),
    y=alt.Y("intrapartum_cs_rate:Q", title="Intrapartum CS rate", axis=alt.Axis(format="%")),
    tooltip=[
        "month:T",
        alt.Tooltip("intrapartum_cs_rate:Q", format=".1%"),
        alt.Tooltip("intended_vaginal_den:Q", title="Intended vaginal births"),
        alt.Tooltip("emergency_cs_count:Q", title="Emergency CS"),
        alt.Tooltip("elective_cs_count:Q", title="Elective CS"),
        alt.Tooltip("births_total:Q", title="Births")
    ]
).properties(height=320)

success_chart = alt.Chart(f).mark_line(point=True).encode(
    x=alt.X("month:T", title="Baby DOB Period"),
    y=alt.Y("vaginal_success_rate:Q", title="Vaginal success rate", axis=alt.Axis(format="%")),
    tooltip=[
        "month:T",
        alt.Tooltip("vaginal_success_rate:Q", format=".1%"),
        alt.Tooltip("intended_vaginal_den:Q", title="Intended vaginal births"),
        alt.Tooltip("nvd_count:Q", title="NVD"),
        alt.Tooltip("births_total:Q", title="Births")
    ]
).properties(height=320)

cA.altair_chart(intra_chart, use_container_width=True)
cB.altair_chart(success_chart, use_container_width=True)

st.caption("Intended vaginal births equals total births minus elective caesareans")
st.caption("Intrapartum CS rate equals emergency caesareans divided by intended vaginal births")
``
st.divider()

c1, c2, c3 = st.columns(3)

vol_chart = alt.Chart(f).mark_bar().encode(
    x=alt.X("month:T", title="Baby DOB Period"),
    y=alt.Y("births_total:Q", title="Births"),
    tooltip=["month:T", "births_total:Q"]
).properties(height=260)

c1.subheader("Birth volume")
c1.altair_chart(vol_chart, use_container_width=True)

f["cs_rate"] = (
    (f["elective_cs_count"] + f["emergency_cs_count"])
    / f["births_total"].replace(0, pd.NA)
)

cs_chart = alt.Chart(f).mark_line(point=True).encode(
    x=alt.X("month:T", title="Baby DOB Period"),
    y=alt.Y("cs_rate:Q", title="C-section rate", axis=alt.Axis(format="%")),
    tooltip=["month:T", alt.Tooltip("cs_rate:Q", format=".1%"), "births_total:Q"]
).properties(height=260)

c2.subheader("C-section rate (headline)")
c2.altair_chart(cs_chart, use_container_width=True)

f["emcs_rate"] = (
    f["emergency_cs_count"]
    / f["births_total"].replace(0, pd.NA)
)

emcs_chart = alt.Chart(f).mark_line(point=True).encode(
    x=alt.X("month:T", title="Baby DOB Period"),
    y=alt.Y("emcs_rate:Q", title="Emergency CS rate", axis=alt.Axis(format="%")),
    tooltip=[
        "month:T",
        alt.Tooltip("emcs_rate:Q", format=".1%"),
        "emergency_cs_count:Q",
        "births_total:Q",
    ],
).properties(height=260)

c3.subheader("Emergency C-section rate")
c3.altair_chart(emcs_chart, use_container_width=True)

st.divider()

mix = f[
    ["month", "nvd_count", "elective_cs_count", "emergency_cs_count"]
].melt(
    id_vars="month",
    var_name="mode",
    value_name="count"
)

mix["mode"] = mix["mode"].replace({
    "nvd_count": "NVD",
    "elective_cs_count": "Elective CS",
    "emergency_cs_count": "Emergency CS"
})

mix_chart = alt.Chart(mix).mark_bar().encode(
    x=alt.X("month:T", title="Baby DOB Period"),
    y=alt.Y("count:Q", title="Count"),
    color=alt.Color("mode:N", title="Mode"),
    tooltip=["month:T", "mode:N", "count:Q"]
).properties(height=320)

st.subheader("Mode of delivery mix (counts)")
st.altair_chart(mix_chart, use_container_width=True)
``
