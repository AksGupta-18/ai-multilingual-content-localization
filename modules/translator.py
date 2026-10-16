import os
import re
from functools import lru_cache

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

try:
    from IndicTransToolkit.processor import IndicProcessor
except ImportError:
    IndicProcessor = None


class TranslationBackend:

    def translate_document(self, text, source_language, target_language):
        raise NotImplementedError("Translation backend must implement translate_document().")


@lru_cache(maxsize=4)
def get_cached_translator(target_language: str):
    return IndicTranslator(target_language=target_language)


class IndicTranslator(TranslationBackend):

    MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"
    _MODEL_CACHE = {}

    LANGUAGE_MAP = {
        "eng_latn": "eng_Latn",
        "eng-latn": "eng_Latn",
        "en": "eng_Latn",
        "english": "eng_Latn",

        "hin_deva": "hin_Deva",
        "hi": "hin_Deva",
        "hindi": "hin_Deva",

        "tel_telu": "tel_Telu",
        "te": "tel_Telu",
        "telugu": "tel_Telu",

        "mar_deva": "mar_Deva",
        "mr": "mar_Deva",
        "marathi": "mar_Deva",

        "tam_taml": "tam_Taml",
        "ta": "tam_Taml",
        "tamil": "tam_Taml",

        "ben_beng": "ben_Beng",
        "bn": "ben_Beng",
        "bengali": "ben_Beng",

        "guj_gujr": "guj_Gujr",
        "gu": "guj_Gujr",
        "gujarati": "guj_Gujr",

        "mal_mlym": "mal_Mlym",
        "ml": "mal_Mlym",
        "malayalam": "mal_Mlym",

        "kan_knda": "kan_Knda",
        "kn": "kan_Knda",
        "kannada": "kan_Knda",

        "pan_guru": "pan_Guru",
        "pa": "pan_Guru",
        "punjabi": "pan_Guru",
    }

    def __init__(
        self,
        model_name: str = None,
        target_language: str = None,
        device: str = None
    ):

        self.device = device or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        if self.device == "cpu":
            torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

            try:
                torch.set_num_interop_threads(1)
            except RuntimeError:
                pass

        self.model_name = model_name or self.MODEL_NAME

        self.model = None
        self.tokenizer = None
        self.processor = None

        self.default_target = self._normalize_target_language(
            target_language or "hi"
        )

        self._load_backend()

    @classmethod
    def _normalize_target_language(cls, language: str) -> str:

        if not language:
            return "hin_Deva"

        normalized = str(language).strip().replace("-", "_")
        key = normalized.lower()

        if key in cls.LANGUAGE_MAP:
            return cls.LANGUAGE_MAP[key]

        return normalized

    @classmethod
    def _resolve_model_name(
        cls,
        _unused_target_language: str = None,
        *args,
        **kwargs
    ) -> str:

        return cls.MODEL_NAME

    @classmethod
    def _get_cache_key(cls, model_name: str, device: str, target_language: str = None):
        # The model is a single shared IndicTrans2 checkpoint. Target language
        # belongs to preprocessing/postprocessing and does not require a
        # second model instance, which would exhaust memory on CPU.
        return (model_name, device)

    @staticmethod
    def _require_processor():
        if IndicProcessor is None:
            raise RuntimeError(
                "IndicTransToolkit is required for IndicTrans2 native-script output. "
                "Install it in the active environment with: "
                "python -m pip install IndicTransToolkit"
            )

    def _load_backend(self):

        self._require_processor()

        cache_key = self.__class__._get_cache_key(
            self.model_name,
            self.device,
            self.default_target,
        )

        cached = self.__class__._MODEL_CACHE.get(cache_key)

        if cached is not None:
            self.model, self.tokenizer, self.processor = cached
            return self.model, self.tokenizer, self.processor

        if self.model is not None and self.tokenizer is not None:

            self.__class__._MODEL_CACHE[cache_key] = (
                self.model,
                self.tokenizer,
                self.processor
            )

            return self.model, self.tokenizer, self.processor

        try:

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )

            # Use FP16 only when NVIDIA CUDA is available.
            # CPU stays on FP32.
            dtype = (
                torch.float16
                if self.device == "cuda"
                else torch.float32
            )

            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_name,
                trust_remote_code=True,
                torch_dtype=dtype
            )

            self.model.to(self.device)
            self.model.eval()

            self.processor = (
                IndicProcessor(inference=True)
                if IndicProcessor is not None
                else None
            )

        except Exception as exc:

            raise RuntimeError(
                f"Failed to load IndicTrans2 model "
                f"'{self.model_name}': {exc}"
            ) from exc

        self.__class__._MODEL_CACHE[cache_key] = (
            self.model,
            self.tokenizer,
            self.processor
        )

        return self.model, self.tokenizer, self.processor

    def _preprocess_sentences(
        self,
        sentences,
        src_lang: str,
        tgt_lang: str
    ):

        if self.processor is None:
            self._require_processor()

        return self.processor.preprocess_batch(
            sentences,
            src_lang=src_lang,
            tgt_lang=tgt_lang
        )

    def _postprocess_translations(
        self,
        decoded,
        lang: str
    ):

        if self.processor is None:
            self._require_processor()

        return self.processor.postprocess_batch(
            decoded,
            lang=lang
        )

    def _split_into_sentences(self, text: str):

        if not text or not text.strip():
            return []

        # Fixed regex only.
        sentences = re.split(
            r"(?<=[.!?])\s+|\n+",
            text.strip()
        )

        return [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

    def _translate_batch(
        self,
        batch,
        src_lang: str,
        tgt_lang: str
    ):

        prepared_batch = self._preprocess_sentences(
            batch,
            src_lang=src_lang,
            tgt_lang=tgt_lang
        )

        inputs = self.tokenizer(
            prepared_batch,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        ).to(self.device)

        with torch.inference_mode():

            generated_tokens = self.model.generate(
                **inputs,
                use_cache=True,
                min_length=0,
                max_length=128,

                # One beam keeps native-script generation reliable on CPU
                # while avoiding the extra generation work that can exhaust
                # the available process resources after model loading.
                num_beams=1,

                num_return_sequences=1,
            )

        with self.tokenizer.as_target_tokenizer():
            decoded = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        translations = self._postprocess_translations(
            decoded,
            lang=tgt_lang
        )
        print("TARGET LANGUAGE:", tgt_lang)
        print("RAW MODEL OUTPUT:", decoded[:1])
        print("POSTPROCESSED OUTPUT:", translations[:1])

        # Release temporary tensors after each batch.
        del inputs
        del generated_tokens

        if self.device == "cuda":
            torch.cuda.empty_cache()

        return [
            item.strip()
            for item in translations
            if item.strip()
        ]

    def translate_document(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:

        if not text or not text.strip():
            return ""

        source_code = self._normalize_target_language(
            source_language or "eng_Latn"
        )

        target_code = self._normalize_target_language(
            target_language or self.default_target
        )

        self.model, self.tokenizer, self.processor = (
            self._load_backend()
        )

        sentences = self._split_into_sentences(text)

        if not sentences:
            return ""

        try:

            if len(sentences) <= 12 and len(text) <= 1800:

                translations = self._translate_batch(
                    sentences,
                    source_code,
                    target_code
                )

                return "\n\n".join(translations).strip()

            translated_parts = []

            current_chunk = []
            current_len = 0

            for sentence in sentences:

                sentence_len = len(sentence)

                if not current_chunk:

                    current_chunk = [sentence]
                    current_len = sentence_len
                    continue

                # Smaller chunks for 16 GB RAM laptops.
                if (
                    len(" ".join(current_chunk + [sentence])) <= 300
                    and len(current_chunk) < 3
                ):

                    current_chunk.append(sentence)
                    current_len += sentence_len

                else:

                    translated_parts.extend(
                        self._translate_batch(
                            current_chunk,
                            source_code,
                            target_code
                        )
                    )

                    current_chunk = [sentence]
                    current_len = sentence_len

            if current_chunk:

                translated_parts.extend(
                    self._translate_batch(
                        current_chunk,
                        source_code,
                        target_code
                    )
                )

            return "\n\n".join(translated_parts).strip()

        except Exception as exc:

            raise RuntimeError(
                f"Translation failed from "
                f"'{source_code}' to '{target_code}' "
                f"using IndicTrans2: {exc}"
            ) from exc