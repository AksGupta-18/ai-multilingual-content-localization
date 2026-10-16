import sys

sys.path.insert(0, r"C:\Users\Curat\Desktop\Ai localization engine")

from modules.translator import IndicTranslator

text = "Machine Learning is used to process large datasets and build predictive models."
translator = IndicTranslator()
print(translator.translate_document(text, "eng_Latn", "hin_Deva"))
