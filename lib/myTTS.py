# import os
import asyncio
import discord
from gtts import gTTS # pip install gTTS
from io import BytesIO
# pip install langid
from lib.lang_detect import detect_language_for_gTTS  # 引入語言偵測函式庫
from pydub import AudioSegment # Please add "/ffmpeg/bin" to system environment variable manually
from lib.audio_queue import audio_queue

async def get_audio(text, language=None):
    # 使用 gTTS 和自動偵測語言
    if language is None:
        language = await detect_language_for_gTTS(text)
    if language is None:
        language = 'zh-TW'
    tts = gTTS(text, lang=language)
    audio = BytesIO()
    tts.write_to_fp(audio)
    audio.seek(0)
    return audio

async def combine_audios(*audios: BytesIO) -> BytesIO:
    """
    將多段音訊合併成一段音訊（串接，不是混音）。
    """
    combined = AudioSegment.empty()

    # 使用 async to_thread 來非同步執行這段同步的 pydub 操作
    def sync_combine():
        nonlocal combined
        for audio_io in audios:
            segment = AudioSegment.from_file(audio_io, format="mp3")
            combined += segment  # 串接音訊
        output = BytesIO()
        combined.export(output, format="mp3")
        output.seek(0)
        return output

    output = await asyncio.to_thread(sync_combine)
    return output

async def play_audio_sync(voice_channel, audio):
    await audio_queue.add_to_queue(voice_channel, audio)
