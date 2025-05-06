import discord
import asyncio
import os

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
        asyncio.run(play_audio(voice_channel, audio))
    else:
        # 如果已經在 event loop 中（例如 Discord bot 運作中），使用 create_task
        asyncio.create_task(play_audio(voice_channel, audio))