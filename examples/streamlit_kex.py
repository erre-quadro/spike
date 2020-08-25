import streamlit as st
from spacy import load
from spacy.displacy import EntityRenderer

from spikex.kex import WikiIdentX
from spikex.wikigraph import WikiGraph

HTML_WRAPPER = """<div style="overflow-x: auto; border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""

HTML_WIKI_HREF_WRAPPER = """<a href="https://{lang}.wikipedia.org/wiki/{page}" target="_blank">{title}</a>"""

st.set_option("deprecation.showfileUploaderEncoding", False)

LANG_EN = "en"
LANG_IT = "it"
LANG_TABLE = {"English": LANG_EN, "Italiano": LANG_IT}


@st.cache(allow_output_mutation=True, show_spinner=False)
def load_en_nlp():
    return load("en_core_web_sm")


@st.cache(allow_output_mutation=True, show_spinner=False)
def load_it_nlp():
    return load("it_core_news_sm")


@st.cache(
    hash_funcs={WikiGraph: id}, allow_output_mutation=True, show_spinner=False
)
def load_en_identx():
    filter_span = lambda x: (
        any(t.pos_ in ("NOUN", "PROPN") for t in x)
        and all(t.pos_ in ("ADJ", "ADV", "NOUN", "PROPN", "VERB") for t in x)
    )
    return WikiIdentX(graph_name="enwiki_core", filter_span=filter_span)


@st.cache(
    hash_funcs={WikiGraph: id}, allow_output_mutation=True, show_spinner=False
)
def load_it_identx():
    filter_span = lambda x: (
        any(t.pos_ in ("NOUN", "PROPN") for t in x)
        and all(t.pos_ in ("ADJ", "ADV", "NOUN", "PROPN", "VERB") for t in x)
    )
    return WikiIdentX(graph_name="itwiki_core", filter_span=filter_span)


@st.cache(allow_output_mutation=True, show_spinner=False)
def load_renderer():
    return EntityRenderer()


def load_nlp(lang):
    if lang == LANG_EN:
        return load_en_nlp()
    elif lang == LANG_IT:
        return load_it_nlp()


def load_identx(lang):
    if lang == LANG_EN:
        return load_en_identx()
    elif lang == LANG_IT:
        return load_it_identx()


def get_html_wiki_hyperlink(title):
    page = title.replace(" ", "_")
    return HTML_WIKI_HREF_WRAPPER.format(lang="it", page=page, title=title)


def get_renderable_idents(wg, idents):
    return [
        {
            "label": get_html_wiki_hyperlink(wg.get_vertex(ident[1])["title"]),
            "start": ident[0].start_char,
            "end": ident[0].end_char,
        }
        for ident in idents
    ]


def main():
    st.title("Knowledge Extraction DEMO")
    lang_key = st.selectbox("Select language", list(LANG_TABLE))
    lang = LANG_TABLE[lang_key]
    nlp = load_nlp(lang)
    identx = load_identx(lang)
    input_text = st.text_area("Insert text")
    st.markdown("#### or")
    uploaded_file = st.file_uploader("Upload a file")
    if input_text:
        text = input_text
    elif uploaded_file is not None:
        text = uploaded_file.read()
    else:
        return
    doc = identx(nlp(text))
    renderer = load_renderer()
    html = renderer.render_ents(
        text, get_renderable_idents(identx.wg, doc._.idents), ""
    )
    st.write(
        HTML_WRAPPER.format(html.replace("\n", "")), unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()