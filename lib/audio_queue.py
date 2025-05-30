import asyncio
import discord
import shutil
import traceback
class AudioQueueManager:
    def __init__(self, voice_bot):
        self.voice_bot = voice_bot
        self.queue = asyncio.Queue()  # 全域播放佇列
        self.is_playing_queue = False
    
    # 將 voice_bot 的屬性和方法暴露給 AudioQueueManager
    @property               # 將方法包裝成屬性
    def voice_client(self): # 當呼叫 self.voice_client 時，實際上是呼叫 voice_bot.voice_client
        return self.voice_bot.voice_client
    @property
    def task_channel(self):
        return self.voice_bot.task_channel
    @voice_client.setter  # 包裝起來的屬性的 setter 方法
    def voice_client(self, value):
        self.voice_bot.voice_client = value
    @task_channel.setter    # 包裝起來的屬性的 setter 方法
    def task_channel(self, value):
        self.voice_bot.task_channel = value

    async def enqueue(self, channel: discord.VoiceChannel, audio_or_player):
        await self.queue.put((channel, audio_or_player))
        if not self.is_playing_queue:
            asyncio.create_task(self.start_playing())

    async def start_playing(self):
        self.is_playing_queue = True
        ffmpeg_path = shutil.which("ffmpeg")

        while not self.queue.empty():
            target_channel, audio_or_player = await self.queue.get()

            if asyncio.iscoroutine(audio_or_player):
                audio_or_player = await audio_or_player
            elif isinstance(audio_or_player, asyncio.Future):
                audio_or_player = await audio_or_player
            elif callable(audio_or_player):
                result = audio_or_player()
                if asyncio.iscoroutine(result):
                    audio_or_player = await result
                else:
                    audio_or_player = result
            try:
                # 如果尚未連線，或在錯誤的頻道，就移動或連線
                if self.voice_client is None or not self.voice_client.is_connected():
                    self.voice_client = await target_channel.connect(reconnect=True, timeout=10)
                elif self.voice_client.channel.id != target_channel.id:
                    await self.voice_client.move_to(target_channel)

                self.voice_client.play(discord.FFmpegPCMAudio(audio_or_player, executable=ffmpeg_path, pipe=True))

                while self.voice_client.is_playing():
                    await asyncio.sleep(0.5)

            except discord.ClientException as e:
                print(f"[audio_queue] ClientException: {e}")
            except Exception as e:
                print(f"[audio_queue] Fail to play audio: [{type(e).__name__}] {e}")
                traceback.print_exc()

        # 播放結束後的處理
        if self.task_channel or not self.queue.empty():
            try:
                if self.voice_client.channel.id != self.task_channel.id:
                    await self.voice_client.move_to(self.task_channel)
            except Exception as e:
                print(f"[audio_queue] Fail to return channel: [{type(e).__name__}] {e}")
        else:
            try:
                await self.voice_client.disconnect()
            except Exception:
                pass
        self.is_playing_queue = False
