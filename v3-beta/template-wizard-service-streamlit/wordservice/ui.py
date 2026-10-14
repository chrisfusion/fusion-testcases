"""The page."""
import streamlit as st

from wordservice import excerpt, words


def render() -> None:
    # Must be the first streamlit call of a run.
    st.set_page_config(page_title="Word counter", page_icon=":material/abc:")
    st.title(":material/abc: Word counter")
    st.caption("Counts the words of a text. Sample: the first paragraphs of Kafka's *Die Verwandlung*.")

    sample = excerpt.load()
    source = st.sidebar.radio("Text", ["Kafka excerpt", "My own text"])
    text = sample if source == "Kafka excerpt" else st.sidebar.text_area("Paste text", height=200)
    top_n = st.sidebar.slider("Words in the chart", 3, 25, 10)

    df = words.count(text)
    if df.empty:
        st.info("No words to count.", icon=":material/info:")
        return

    total = int(df["count"].sum())
    cols = st.columns(3)
    cols[0].metric("words", total)
    cols[1].metric("distinct", len(df))
    cols[2].metric("most frequent", f"{df.iloc[0]['word']} ({df.iloc[0]['count']})")

    st.bar_chart(df.head(top_n).set_index("word")["count"], y_label="occurrences")

    query = st.text_input("Look up a word", placeholder="gregor").strip().lower()
    table = df[df["word"].str.contains(query, regex=False)] if query else df
    st.dataframe(table, hide_index=True, width="stretch")
