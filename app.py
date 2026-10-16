import os
import tempfile
from pathlib import Path

import streamlit as st

from modules.localization import run_localization

st.set_page_config(
    page_title="AI Localization Engine",
    page_icon="📚",
    layout="wide",
)

TARGET_LANGUAGE_MAP = {
    "Hindi": "hin_Deva",
    "Telugu": "tel_Telu",
    "Marathi": "mar_Deva",
    "Tamil": "tam_Taml",
    "Bengali": "ben_Beng",
    "Gujarati": "guj_Gujr",
    "Malayalam": "mal_Mlym",
    "Kannada": "kan_Knda",
    "Punjabi": "pan_Guru",
}

st.title("AI-Powered Multilingual Content Localization Engine")
st.caption("Engineering educational content localization for skill courses")

with st.sidebar:
    st.header("Project Details")
    st.markdown(
        "- Upload engineering course content in PDF, DOCX, PPTX, or TXT format\n"
        "- Detect the source language automatically\n"
        "- Select a target Indian regional language\n"
        "- Translate and review the localized output"
    )

uploaded_file = st.file_uploader(
    "Upload an engineering course document",
    type=["pdf", "docx", "pptx", "txt"],
    help="Supported formats: PDF, DOCX, PPTX, and TXT",
)

selected_language_label = st.selectbox(
    "Select target language",
    options=list(TARGET_LANGUAGE_MAP.keys()),
    index=0,
)
selected_language_code = TARGET_LANGUAGE_MAP[selected_language_label]

if uploaded_file is not None:
    st.info(f"Uploaded file: {uploaded_file.name}")

if "result" not in st.session_state:
    st.session_state.result = None

if "last_selected_language" not in st.session_state:
    st.session_state.last_selected_language = selected_language_label

if st.session_state.last_selected_language != selected_language_label:
    st.session_state.result = None
    st.session_state.last_selected_language = selected_language_label

translate_button = st.button("Translate")

if translate_button:
    if uploaded_file is None:
        st.warning("Please upload a document before translating.")
    else:
        try:
            suffix = Path(uploaded_file.name).suffix or ".txt"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(uploaded_file.getvalue())
                temp_path = temp_file.name

            with st.spinner("Translating... this may take a little while for large documents."):
                result = run_localization(
                    file_path=temp_path,
                    target_language=selected_language_code,
                )
            st.session_state.result = result
            os.unlink(temp_path)

            st.success("Localization completed successfully.")
        except Exception as exc:  # pragma: no cover - UI-level safety
            st.error(f"Translation failed: {exc}")
            st.session_state.result = None

result = st.session_state.result

if result:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Detected source language")
        st.write(result["source_language"])
        st.subheader("Original / Extracted Text")
        st.text_area(
            label="Original Content",
            value=result["extracted_text"],
            height=350,
            key="original_text",
        )

    with col2:
        st.subheader("Target language")
        st.write(result["target_language"] or selected_language_label)
        st.subheader("Translated / Localized Text")
        st.text_area(
            label="Translated Content",
            value=result["translated_text"],
            height=350,
            key="translated_text",
        )
else:
    st.info("Upload a document and click Translate to begin.")
