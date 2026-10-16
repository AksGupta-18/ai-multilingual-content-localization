from langdetect import detect, LangDetectException


LANGUAGE_ALIASES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "mr": "Marathi",
    "ta": "Tamil",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ml": "Malayalam",
    "kn": "Kannada",
    "pa": "Punjabi",
}


def detect_language(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return "unknown"

    if len(cleaned) < 15:
        return "en"

    try:
        detected_code = detect(cleaned)
        return detected_code.lower()
    except LangDetectException:
        return "unknown"


def get_language_label(language_code: str) -> str:
    return LANGUAGE_ALIASES.get(language_code.lower(), language_code.upper())
