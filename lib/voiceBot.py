import asyncio
from lib.chat_listener import ChatListener
from lib import yt_url, lang_detect, myTTS
from lib.audio_queue import AudioQueueManager

import discord
from typing import Optional

class VoiceBot:
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None  # discord.VoiceClient 實例
        self.read_mode = False
        self.chat_reader = None  # 用於存儲 ChatListener 實例
        self.join_lock = asyncio.Lock()  # 防止重複 join
        # 用來載入伺服器設定 bot.guild_config 若 bot 無此屬性則使用空字典 
        self.guild_config = getattr(bot, "guild_config", {})
        # 建立實例
        self.task_channel: Optional[discord.VoiceChannel] = None # 用來存儲任務頻道
        self.audio_queue = AudioQueueManager(self)

    async def join(self, ctx):
        """讓機器人加入使用者所在的語音頻道"""
        async with self.join_lock:
            if ctx.author.voice is None:
                return "請先加入語音頻道。"
            user_voice_channel = ctx.author.voice.channel
            if self.voice_client and self.voice_client.is_connected():
                if self.voice_client.channel.id != user_voice_channel.id:
                    await self.voice_client.move_to(user_voice_channel)
                    self.task_channel = self.voice_client.channel
                else:
                    return "已經在語音頻道中。"
            else:
                try:
                    if self.voice_client:
                        await self.voice_client.disconnect(force=True) # 保險措施：確保沒有殘留連線
                    self.voice_client = await user_voice_channel.connect(reconnect=True, timeout=10)
                    self.task_channel = self.voice_client.channel
                except asyncio.TimeoutError:
                    return "連接語音頻道超時，請稍後再試。"
                except discord.ClientException as e:
                    return f"加入語音頻道失敗：{e}"

            return f"已加入語音頻道：{self.voice_client.channel.name}"

    async def leave(self, ctx):
        """讓機器人離開語音頻道"""
        if ctx.voice_client:
            self.task_channel = None
            self.read_mode = False
            await ctx.voice_client.disconnect()
            self.voice_client = None
            return "已離開語音頻道。"
        else:
            return "機器人未在語音頻道中。"

    async def say_yt_chat(self, ctx, url):
        """朗讀YouTube聊天室內容"""
        msg = await self.join(ctx)  # 確保已加入語音頻道
        await ctx.send(msg, delete_after=3)

        video_id = await yt_url.get_vid(url)
        if video_id is None:
            return "請輸入有效的 YouTube 直播網址。"

        if self.chat_reader and self.chat_reader.chat is not None:
            self.chat_reader.stop() # 停止之前的聊天室讀取
            await ctx.send("已停止之前的聊天室朗讀。", delete_after = 3)

        # 初始化 ChatListener 並以非阻塞方式啟動聊天室讀取
        self.chat_reader = ChatListener(video_id, self, self.voice_client.channel)
        asyncio.create_task(self.chat_reader.start(ctx)) # 使用 asyncio.create_task 來非阻塞地啟動
        return "開始朗讀聊天室。"

    async def stop_yt_chat(self, ctx):
        """停止朗讀YouTube聊天室內容"""
        if self.chat_reader is not None:
            self.chat_reader.stop()  # 停止聊天室讀取
            self.chat_reader = None
            return "已停止朗讀聊天室。"
        else:
            return "無正在朗讀的聊天室"

    async def say(self, ctx, *, text):
        """朗讀指定的文字"""
        msg = await self.join(ctx)  # 確保已加入語音頻道
        await ctx.send(msg, delete_after=3)
        if not text:
            return f"請輸入要朗讀的文字。格式：`{ctx.prefix}say <text>`"
        try:
            language = await lang_detect.detect_language_for_gTTS(text)
            audio = await myTTS.get_audio(text, language)
            await self.audio_queue.enqueue(self.voice_client.channel, audio)
            return None
        except Exception as e:
            return f"朗讀錯誤：{e}"
    async def read_out(self, ctx):
        """啟用朗讀模式"""
        msg = await self.join(ctx)  # 確保已加入語音頻道
        await ctx.send(msg, delete_after=3)
        self.read_mode = True
        return "🔊 朗讀模式已啟用"

    async def no_read_out(self, ctx):
        """停用朗讀模式"""
        self.read_mode = False
        return "🔇 朗讀模式已停用"
    
    async def shutdown(self, ctx):
        """關閉機器人"""
        await asyncio.sleep(5)  # 等待5秒鐘以確保其他任務完成
        await self.bot.close()

    async def helps(self, ctx, prefix: str = ">"):
        """顯示幫助訊息"""
        help_message = (
            "🔊 朗讀機器人指令列表：",
            ">>> 指令列表：",
            f"- `{prefix}helps`",
            "    - 顯示指令列表",
            f"- `{prefix}join`",
            "    - 讓機器人加入語音頻道",
            f"- `{prefix}leave`",
            "    - 讓機器人離開語音頻道",
            f"- `{prefix}say_yt_chat <YouTube直播網址>`",
            "    - 朗讀YouTube聊天室內容",
            f"- `{prefix}stop_yt_chat`",
            "    - 停止朗讀YouTube聊天室內容",
            f"- `{prefix}say <文字>`",
            "    - 朗讀指定的文字",
            f"- `{prefix}readout`",
            "    - 啟用朗讀模式(播報伺服器訊息)",
            f"- `{prefix}noreadout`",
            "    - 停用朗讀模式",
            f"- `{prefix}shutdown`",
            "    - 關閉機器人",
        )
        return help_message