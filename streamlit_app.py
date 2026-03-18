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
        "elective_cs_count",
        "emergency_cs_count"
    ]

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

births = int(f["births_total"].sum())
cs_total = int((f["elective_cs_count"] + f["emergency_cs_count"]).sum())
emcs_total = int(f["emergency_cs_count"].sum())

cs_rate = cs_total / max(1, births)
emcs_rate = emcs_total / max(1, births)

k1, k2, k3 = st.columns(3)
k1.metric("Births (total)", births)
k2.metric("C-section rate", f"{cs_rate:.1%}")
k3.metric("Emergency C-section rate", f"{emcs_rate:.1%}")

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
