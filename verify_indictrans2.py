from modules.translator import IndicTranslator
print(IndicTranslator.MODEL_NAME)
print(IndicTranslator._resolve_model_name('hi'))
print(IndicTranslator._normalize_target_language('hi'))
print(IndicTranslator._normalize_target_language('eng_Latn'))
