import asyncio
from collections import defaultdict
import discord
import shutil

class AudioQueueManager:
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)  # 每個語音頻道一個佇列
        self.playing_flags = defaultdict(lambda: False)

    async def enqueue(self, voice_client: discord.VoiceClient, audio):
        queue = self.queues[voice_client.channel.id]
        await queue.put((voice_client, audio))
        if not self.playing_flags[voice_client.channel.id]:
            asyncio.create_task(self.start_playing(voice_client.channel.id))

    def is_empty(self) -> bool:
        return not self.queue

    async def start_playing(self, channel_id):
        self.playing_flags[channel_id] = True
        queue = self.queues[channel_id]

        while not queue.empty():
            voice_client, audio = await queue.get()
            if not voice_client.is_connected():
                # 嘗試重新加入語音頻道
                try:
                    target_channel = voice_client.channel  # 取得原本的語音頻道
                    voice_client = await target_channel.connect()
                    print(f"[audio_queue] Bot 重新加入語音頻道 {target_channel.name}")
                except discord.ClientException:
                    print("[audio_queue] 無法重新加入語音頻道，可能已被踢出或缺權限")
                    continue
            try:
                ffmpeg_path = shutil.which("ffmpeg")
                voice_client.play(discord.FFmpegPCMAudio(source=audio, executable=ffmpeg_path, pipe=True))
                while voice_client.is_playing():
                    await asyncio.sleep(0.5)
            except Exception as e:
                print(f"[audio_queue] 播放音訊時發生錯誤: [{type(e).__name__}] {e}")
                continue
        self.playing_flags[channel_id] = False

# 建立實例
audio_queue = AudioQueueManager()
