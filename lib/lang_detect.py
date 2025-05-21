import langid
from langid.langid import LanguageIdentifier, model

# 建立支援語言的對應表（langid -> gTTS）
langid_to_gtts_map = {
    "he": "iw", "jv": "jw", "zh": "zh-TW", "pt": "pt-PT",
    "nb": "no", "nn": "no", "no": "no"
}

# gTTS 支援的語言代碼
supported_gtts_langs = {
    "af", "am", "ar", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de",
    "el", "en", "es", "et", "eu", "fi", "fr", "fr-CA", "gl", "gu", "ha",
    "hi", "hr", "hu", "id", "is", "it", "iw", "ja", "jw", "km", "kn", "ko",
    "la", "lt", "lv", "ml", "mr", "ms", "my", "ne", "nl", "no", "pa", "pl",
    "pt", "pt-PT", "pt-BR", "ro", "ru", "si", "sk", "sq", "sr", "su", "sv",
    "sw", "ta", "te", "th", "tl", "tr", "uk", "ur", "vi", "yue", "zh-CN", "zh-TW", "zh"
}

# 初始化分類器
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

# 全面開放 langid 支援語言
langid.set_languages(None)

async def detect_language_for_gTTS(text):
    lang, prob = identifier.classify(text)
    lang = langid_to_gtts_map.get(lang, lang)
    if lang in supported_gtts_langs:
        return lang
    return 'en' # 如果不支援，預設為英文
