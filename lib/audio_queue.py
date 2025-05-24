import asyncio
from collections import deque
from typing import Deque, Tuple, Dict
import shutil
import discord

class AudioQueueManager:
    def __init__(self):
        self.queue: Deque[Tuple[int, discord.VoiceChannel, bytes]] = deque()  # guild_id, voice_channel, audio_bytes
        self.playing_flags: Dict[int, bool] = {}  # guild_id: is_playing
        self.locks: Dict[int, asyncio.Lock] = {}  # guild_id: lock

    def enqueue(self, voice_channel: discord.VoiceChannel, audio: bytes):
        guild_id = voice_channel.guild.id
        self.queue.append((guild_id, voice_channel, audio))

    def is_empty(self) -> bool:
        return not self.queue

    async def start_playing(self, bot: discord.Client):
        while self.queue:
            guild_id, voice_channel, audio = self.queue.popleft()

            if guild_id not in self.locks:
                self.locks[guild_id] = asyncio.Lock()
            lock = self.locks[guild_id]

            async with lock:
                if self.playing_flags.get(guild_id, False):
                    continue
                self.playing_flags[guild_id] = True

                try:
                    voice_client = await voice_channel.connect()
                    print(f"[AudioQueue] 加入語音頻道：{voice_channel.name}")
                except discord.ClientException:
                    print(f"[AudioQueue] 無法加入語音頻道：{voice_channel.name}")
                    self.playing_flags[guild_id] = False
                    continue
                try:
                    ffmpeg_path = shutil.which("ffmpeg")
                    audio_source = discord.FFmpegPCMAudio(source=audio, executable=ffmpeg_path, pipe=True)
                    voice_client.play(audio_source)

                    while voice_client.is_playing():
                        await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"[audio_queue] 播放音訊時發生錯誤: [{type(e).__name__}] {e}")
                    continue

                self.playing_flags[guild_id] = False

# 建立實例
audio_queue = AudioQueueManager()
