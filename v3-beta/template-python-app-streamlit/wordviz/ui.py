"""The page: layout and widgets."""
import streamlit as st

from wordviz import data, theme


def render() -> None:
    # Must be the first streamlit call. page_icon accepts an emoji, a material
    # icon (":material/bar_chart:") or - as here - a picture from the assets.
    st.set_page_config(
        page_title="Word Count",
        page_icon=theme.path("favicon.png"),
        layout="wide",
    )
    theme.apply_css()
    st.image(theme.path("banner.png"), width="stretch")

    text = _sidebar_text()
    words = data.split_words(text)
    if not words:
        st.info("No text to analyse.", icon=":material/info:")
        return

    # The three cards use our own svg icons from assets/icons.
    cols = st.columns(3)
    cols[0].markdown(theme.metric_card("words", str(len(words)), "words"), unsafe_allow_html=True)
    cols[1].markdown(theme.metric_card("distinct", str(len(set(words))), "distinct words"), unsafe_allow_html=True)
    cols[2].markdown(theme.metric_card("size", f"{len(text.encode('utf-8'))} B", "text size"), unsafe_allow_html=True)

    st.write("")
    top_n = st.sidebar.slider("Words in the chart", 3, 15, 8)
    drop_stopwords = st.sidebar.toggle("Hide common words", value=True)

    # Tab labels use built-in material icons - no asset needed for those.
    tab_top, tab_len, tab_text = st.tabs([
        ":material/bar_chart: Top words",
        ":material/straighten: Word lengths",
        ":material/description: Text",
    ])
    with tab_top:
        st.bar_chart(data.top_words(words, top_n, drop_stopwords), y_label="occurrences")
    with tab_len:
        st.bar_chart(data.length_distribution(words), y_label="words")
    with tab_text:
        st.text(text)


def _sidebar_text() -> str:
    """Input: the bundled sample (an asset) or text typed by the user."""
    st.sidebar.header(":material/edit_note: Input")
    source = st.sidebar.radio("Text source", ["Bundled sample", "My own text"])
    sample = theme.read_text("words.txt")
    if source == "Bundled sample":
        return sample
    return st.sidebar.text_area("Paste text", value=sample, height=200)
