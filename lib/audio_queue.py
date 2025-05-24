import asyncio
import discord
import shutil
from typing import Optional

class AudioQueueManager:
    def __init__(self):
        self.queue = asyncio.Queue()  # 全域播放佇列
        self.is_playing = False
        self.voice_client: Optional[discord.VoiceClient] = None
        self.task_channel: Optional[discord.VoiceChannel] = None  # 任務頻道

    async def enqueue(self, channel: discord.VoiceChannel, audio_path: str):
        await self.queue.put((channel, audio_path))
        if not self.is_playing:
            asyncio.create_task(self.start_playing())

    async def start_playing(self):
        self.is_playing = True

        while not self.queue.empty():
            target_channel, audio_path = await self.queue.get()

            try:
                # 如果尚未連線，或在錯誤的頻道，就移動或連線
                if self.voice_client is None or not self.voice_client.is_connected():
                    self.voice_client = await target_channel.connect()
                elif self.voice_client.channel.id != target_channel.id:
                    await self.voice_client.move_to(target_channel)

                ffmpeg_path = shutil.which("ffmpeg")
                self.voice_client.play(discord.FFmpegPCMAudio(audio_path, executable=ffmpeg_path))

                while self.voice_client.is_playing():
                    await asyncio.sleep(0.5)

            except discord.ClientException as e:
                print(f"[audio_queue] ClientException: {e}")
            except Exception as e:
                print(f"[audio_queue] 播放音訊時發生錯誤: [{type(e).__name__}] {e}")

        # 播放結束後的處理
        if self.task_channel:
            try:
                await self.voice_client.move_to(self.task_channel)
            except Exception as e:
                print(f"[audio_queue] 返回任務頻道失敗: {e}")
        else:
            try:
                await self.voice_client.disconnect()
            except Exception:
                pass
        self.is_playing = False

# 建立實例
audio_queue = AudioQueueManager()
