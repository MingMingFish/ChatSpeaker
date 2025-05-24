# lib/audio_queue.py
import asyncio
from collections import defaultdict
import discord
import shutil

class AudioQueueManager:
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)  # 每個語音頻道一個佇列
        self.playing_flags = defaultdict(lambda: False)

    async def add_to_queue(self, voice_client: discord.VoiceClient, audio):
        queue = self.queues[voice_client.channel.id]
        await queue.put((voice_client, audio))
        if not self.playing_flags[voice_client.channel.id]:
            asyncio.create_task(self._start_playing(voice_client.channel.id))

    async def _start_playing(self, channel_id):
        self.playing_flags[channel_id] = True
        queue = self.queues[channel_id]

        while not queue.empty():
            voice_client, audio = await queue.get()
            if not voice_client.is_connected():
                break
            ffmpeg_path = shutil.which("ffmpeg")
            voice_client.play(discord.FFmpegPCMAudio(source=audio, executable=ffmpeg_path, pipe=True))
            while voice_client.is_playing():
                await asyncio.sleep(0.5)
            await asyncio.sleep(0.3)

        self.playing_flags[channel_id] = False
        # 若佇列空了且 bot 在語音中沒特別設置常駐，可自動離開（由調用端決定）

audio_queue = AudioQueueManager()
