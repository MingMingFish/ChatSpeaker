import asyncio
from lib import chat_listener
from lib import yt_url, lang_detect, bot_audio, myTTS

class VoiceBot:
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None  # discord.VoiceClient 實例
        self.read_mode = False
        self.chat_reader = None  # 用於存儲 ChatListener 實例

    async def join(self, ctx):
        """讓機器人加入使用者所在的語音頻道"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                self.voice_client = await channel.connect()
                return "已加入語音頻道。"
            else:
                return "已經在語音頻道中。"
        else:
            return "請先加入語音頻道。"

    async def leave(self, ctx):
        """讓機器人離開語音頻道"""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.voice_client = None
            self.read_mode = False
            return "已離開語音頻道。"
        else:
            return "機器人未在語音頻道中。"

    async def say_yt_chat(self, ctx, url):
        """朗讀YouTube聊天室內容"""
        if ctx.voice_client is None:
            if ctx.author.voice:
                voice_channel = ctx.author.voice.channel
                self.voice_client = await voice_channel.connect()
            else:
                return "請先加入語音頻道。"

        video_id = await yt_url.get_vid(url)
        if video_id is None:
            return "請輸入有效的 YouTube 直播網址。"

        if self.chat_reader is not None:
            self.chat_reader.stop() # 停止之前的聊天室讀取
            await ctx.send("已停止之前的聊天室朗讀。", delete_after = 3)

        # 初始化 ChatListener 並以非阻塞方式啟動聊天室讀取
        self.chat_reader = chat_listener.ChatListener(video_id, self, self.voice_client)
        asyncio.create_task(self.chat_reader.start())  # 使用 asyncio.create_task 來非阻塞地啟動
        return "開始朗讀聊天室。"

    async def stop_yt_chat(self):
        """停止朗讀YouTube聊天室內容"""
        self.chat_reader.stop()  # 停止聊天室讀取
        return "已停止朗讀聊天室。"

    async def say(self, ctx, *, text):
        """朗讀指定的文字"""
        if ctx.author.voice is None:
            return "請先加入語音頻道。"

        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            bot_voice_channel = await voice_channel.connect()
            print(f"Joined voice channel: {voice_channel.name}")
        else:
            bot_voice_channel = ctx.voice_client

        language = lang_detect.detect_language_for_gTTS(text)
        audio = myTTS.get_audio(text, language)
        await bot_audio.play_audio_sync(bot_voice_channel, audio)
        return None
    async def readout(self, ctx):
        """啟用朗讀模式"""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if ctx.voice_client is None:
                self.voice_client = await channel.connect()
                self.read_mode = True
                return "🔊 朗讀模式已啟用"
        else:
            return "請先加入語音頻道。"

    async def noreadout(self):
        """停用朗讀模式"""
        self.read_mode = False
        return "🔇 朗讀模式已停用"
    
    async def shutdown(self, ctx):
        """關閉機器人"""
        await asyncio.sleep(5)  # 等待3秒鐘以確保其他任務完成
        await self.bot.close()

    async def helps():
        """顯示幫助訊息"""
        help_message = (
            "🔊 朗讀機器人指令列表：",
            ">>> 指令列表：",
            "- `>help`",
            "    - 顯示指令列表",
            "- `>join`",
            "    - 讓機器人加入語音頻道",
            "- `>leave`",
            "    - 讓機器人離開語音頻道",
            "- `>say_yt_chat <YouTube直播網址>`",
            "    - 朗讀YouTube聊天室內容",
            "- `>stop_yt_chat`",
            "    - 停止朗讀YouTube聊天室內容",
            "- `>say <文字>`",
            "    - 朗讀指定的文字",
            "- `>readout`",
            "    - 啟用朗讀模式(播報伺服器訊息)",
            "- `>noreadout`",
            "    - 停用朗讀模式",
            "- `>shutdown`",
            "    - 關閉機器人",
        )
        return help_message