from modules.translator import IndicTranslator

print(IndicTranslator._normalize_target_language('tel_Telu'))
print(IndicTranslator._normalize_target_language('hin_Deva'))
print(IndicTranslator._get_cache_key(IndicTranslator.MODEL_NAME, 'cpu', 'hin_Deva'))
print(IndicTranslator._get_cache_key(IndicTranslator.MODEL_NAME, 'cpu', 'tel_Telu'))
print(IndicTranslator._get_cache_key(IndicTranslator.MODEL_NAME, 'cpu', 'hin_Deva') != IndicTranslator._get_cache_key(IndicTranslator.MODEL_NAME, 'cpu', 'tel_Telu'))
