import pytest

import modules.translator as translator_module


def test_uses_indictrans2_model_for_indian_languages():
    assert translator_module.IndicTranslator.MODEL_NAME == "ai4bharat/indictrans2-en-indic-dist-200M"
    assert translator_module.IndicTranslator._resolve_model_name(None, "hi") == "ai4bharat/indictrans2-en-indic-dist-200M"
    assert translator_module.IndicTranslator._resolve_model_name(None, "te") == "ai4bharat/indictrans2-en-indic-dist-200M"
    assert "Helsinki-NLP" not in translator_module.IndicTranslator._resolve_model_name(None, "hi")


def test_translator_handles_missing_indictrans_toolkit_gracefully():
    assert hasattr(translator_module.IndicTranslator, "_normalize_target_language")
    assert translator_module.IndicTranslator._normalize_target_language("hi") == "hin_Deva"
    assert translator_module.IndicTranslator._normalize_target_language("eng_Latn") == "eng_Latn"


def test_model_cache_is_shared_across_target_languages():
    hi_key = translator_module.IndicTranslator._get_cache_key(
        translator_module.IndicTranslator.MODEL_NAME,
        "cpu",
        "hin_Deva",
    )
    tel_key = translator_module.IndicTranslator._get_cache_key(
        translator_module.IndicTranslator.MODEL_NAME,
        "cpu",
        "tel_Telu",
    )

    assert hi_key == tel_key


def test_missing_indictrans_toolkit_raises_clear_error(monkeypatch):
    original_processor = translator_module.IndicProcessor
    monkeypatch.setattr(translator_module, "IndicProcessor", None)

    with pytest.raises(RuntimeError, match="IndicTransToolkit"):
        translator_module.IndicTranslator._require_processor()

    monkeypatch.setattr(translator_module, "IndicProcessor", original_processor)
