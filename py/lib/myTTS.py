import os
import asyncio
import discord
from gtts import gTTS # pip install gTTS
from io import BytesIO
# pip install langid
from lib.lang_detect import detect_language_for_gTTS  # 引入語言偵測函式庫
from pydub import AudioSegment # Please add "/ffmpeg/bin" to system environment variable manually

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

async def play_audio(channel, audio):
    ffmpeg_path = os.path.join("tools", "ffmpeg.exe")
    while channel.is_playing():
        await asyncio.sleep(1)
    channel.play(discord.FFmpegPCMAudio(source=audio, executable=ffmpeg_path, pipe=True))

async def play_audio_sync(voice_channel, audio):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # 如果沒有 event loop，就建立一個新的（通常發生在主線程）
        await asyncio.run(play_audio(voice_channel, audio))
    else:
        # 如果已經在 event loop 中（例如 Discord bot 運作中），使用 create_task
        await asyncio.create_task(play_audio(voice_channel, audio))