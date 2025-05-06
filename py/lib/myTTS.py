from gtts import gTTS # pip install gTTS
from io import BytesIO
# pip install langid
from lib.lang_detect import detect_language_for_gTTS  # 引入語言偵測函式庫

def get_audio(text, language=None):
    # 使用 gTTS 和自動偵測語言
    if language is None:
        language = detect_language_for_gTTS(text)
    if language is None:
        language = 'zh-TW'
    # 這裡原本的 gTTS 使用邏輯，保持不變
    # speaks without saving the audio file
    tts = gTTS(text, lang=language)
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio
