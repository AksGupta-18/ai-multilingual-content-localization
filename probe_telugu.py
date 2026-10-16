from modules.translator import IndicTranslator

text = 'Welcome! This is a sample sentence for testing.'
for target in ['hin_Deva', 'tel_Telu', 'tam_Taml']:
    translator = IndicTranslator(target_language=target)
    out = translator.translate_document(text, 'eng_Latn', target)
    print('TARGET=', target)
    print(out)
    print('---')
