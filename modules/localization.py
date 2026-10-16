from .detector import detect_language, get_language_label
from .extractor import extract_text_from_file
from .preprocess import preprocess_text, restore_technical_terms
from .translator import get_cached_translator


def map_language_code(language_name_or_code: str) -> str:
    normalized = (language_name_or_code or "").lower().strip()

    if normalized in {"english", "en", "eng_latn", "eng-latn"}:
        return "eng_Latn"
    if normalized in {"hindi", "hi"}:
        return "hin_Deva"
    if normalized in {"telugu", "te"}:
        return "tel_Telu"
    if normalized in {"marathi", "mr"}:
        return "mar_Deva"
    if normalized in {"tamil", "ta"}:
        return "tam_Taml"
    if normalized in {"bengali", "bn"}:
        return "ben_Beng"
    if normalized in {"gujarati", "gu"}:
        return "guj_Gujr"
    if normalized in {"malayalam", "ml"}:
        return "mal_Mlym"
    if normalized in {"kannada", "kn"}:
        return "kan_Knda"
    if normalized in {"punjabi", "pa"}:
        return "pan_Guru"
    if normalized in {"unknown", "", "none", "null"}:
        return "eng_Latn"
    return "eng_Latn"


def run_localization(file_path: str, target_language: str):
    extracted_text = extract_text_from_file(file_path)
    if not extracted_text.strip():
        raise ValueError("No text could be extracted from the uploaded file.")

    prepared_data = preprocess_text(extracted_text)
    detected_language = detect_language(prepared_data["text"])
    detected_language_label = get_language_label(detected_language)

    translator = get_cached_translator(target_language)
    translated_text = translator.translate_document(
        prepared_data["text"],
        source_language=map_language_code(detected_language),
        target_language=target_language,
    )

    final_text = restore_technical_terms(translated_text, prepared_data["protected_terms"])

    return {
        "extracted_text": extracted_text,
        "source_language": detected_language_label,
        "target_language": target_language,
        "translated_text": final_text,
    }
