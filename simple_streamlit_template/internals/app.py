import numpy as np
import pandas as pd
import streamlit as st

st.title("Falling Numbers Demo")
st.caption("100 random values with a downward trend and 10-point rolling average")

rng = np.random.default_rng(seed=7)
n = 100
trend = np.linspace(0, -20, n)
noise = rng.normal(0, 3, n)
values = 70 + trend + noise

df = pd.DataFrame({"value": values})
df["rolling_avg"] = df["value"].rolling(window=10, min_periods=1).mean()

col1, col2, col3 = st.columns(3)
col1.metric("Min", f"{values.min():.1f}")
col2.metric("Max", f"{values.max():.1f}")
col3.metric("Mean", f"{values.mean():.1f}")

st.line_chart(df, y=["value", "rolling_avg"])
