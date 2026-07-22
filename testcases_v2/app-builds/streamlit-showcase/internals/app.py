import numpy as np
import pandas as pd
import streamlit as st

st.title("Weave Showroom")
st.caption("Simulated WeaveRun throughput across chain step kinds")

rng = np.random.default_rng(seed=42)
kinds = ["Job", "Deploy"]
hours = pd.date_range("2026-01-01", periods=24, freq="h")

df = pd.DataFrame(
    {
        "hour": np.tile(hours, len(kinds)),
        "stepKind": np.repeat(kinds, len(hours)),
        "runs": rng.poisson(lam=12, size=len(hours) * len(kinds)),
    }
)

pivot = df.pivot(index="hour", columns="stepKind", values="runs")

col1, col2, col3 = st.columns(3)
col1.metric("Total runs", int(pivot.sum().sum()))
col2.metric("Peak hour", int(pivot.sum(axis=1).max()))
col3.metric("Job / Deploy split", f"{pivot['Job'].sum()} / {pivot['Deploy'].sum()}")

st.bar_chart(pivot)
