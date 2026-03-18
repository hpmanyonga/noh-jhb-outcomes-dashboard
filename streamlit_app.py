@st.cache_data
def load_data():
    df = pd.read_csv("data/jhb_outcomes_monthly.csv", parse_dates=["month"])
    df = df.sort_values("month")
    return df
``
