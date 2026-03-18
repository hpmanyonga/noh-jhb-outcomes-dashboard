@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/jhb_outcomes_monthly.csv",
        sep=",",
        engine="python",
        encoding="utf-8-sig",
        on_bad_lines="skip"
    )

    # Ensure expected columns exist
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
``
