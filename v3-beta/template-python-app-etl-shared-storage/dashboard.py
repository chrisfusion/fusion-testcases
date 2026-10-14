"""Process 3 of 3 (ENTRYPOINT=dashboard.py, runner type streamlit): visualise the word count.

Reads /weave-shared/wordcount.csv, written by count.py. This is a long-running web
app, so it runs as a *run-owned deploy step* - only those get the shared storage
mounted (see README.md). `streamlit run` executes this file again on every
interaction, hence the work is cheap: read one csv, draw.
"""
import pandas as pd
import streamlit as st

from kafka_etl import counting, paths

st.set_page_config(page_title="Die Verwandlung - Word Count", page_icon=":material/menu_book:", layout="wide")
st.title(":material/menu_book: Die Verwandlung - Word Count")
st.caption("Franz Kafka, Project Gutenberg #22367 · extract → count → this dashboard, linked by shared storage")

try:
    rows = counting.read_wordcount(paths.WORDCOUNT_FILE)
except FileNotFoundError:
    st.error(f"{paths.WORDCOUNT_FILE} does not exist yet - did the `count` step finish?", icon=":material/error:")
    st.stop()

df = pd.DataFrame(rows, columns=["word", "count"])
df["letters"] = df["word"].str.len()

total = int(df["count"].sum())
cols = st.columns(3)
cols[0].metric("words", f"{total:,}")
cols[1].metric("distinct words", f"{len(df):,}")
cols[2].metric("most frequent", f"{df.iloc[0]['word']} ({df.iloc[0]['count']})")

top_n = st.sidebar.slider("Words in the chart", 5, 50, 20)
min_letters = st.sidebar.slider("Minimum word length", 1, 10, 4,
                                help="Raise it to hide short filler words like 'und', 'der', 'es'.")
query = st.sidebar.text_input("Look up a word", placeholder="gregor")

tab_top, tab_len, tab_table = st.tabs([
    ":material/bar_chart: Top words",
    ":material/straighten: Word lengths",
    ":material/table: All words",
])
with tab_top:
    shown = df[df["letters"] >= min_letters].head(top_n)
    st.bar_chart(shown.set_index("word")["count"], y_label="occurrences")
with tab_len:
    # Occurrences per word length: how long are the words Kafka uses?
    st.bar_chart(df.groupby("letters")["count"].sum(), x_label="letters", y_label="occurrences")
with tab_table:
    table = df[df["word"].str.contains(query.lower(), regex=False)] if query else df
    st.dataframe(table[["word", "count"]], hide_index=True, width="stretch")
