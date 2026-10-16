from modules.translator import IndicTranslator

samples = [
    "This is a sample sentence for testing translation quality.",
    "The project is ready for the final presentation.",
    "Machine learning helps us analyze large amounts of text."
]

languages = ["hi", "te", "ta", "bn", "gu", "ml"]

translator = IndicTranslator(target_language="hi")

for lang in languages:
    print(f"\n--- {lang.upper()} ---")
    for text in samples:
        try:
            translated = translator.translate_document(text, "eng_Latn", lang)
            print(f"EN -> {lang}: {translated}")
        except Exception as exc:
            print(f"EN -> {lang}: ERROR: {type(exc).__name__}: {exc}")
            break
