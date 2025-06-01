import asyncio
from lib.chat_listener import ChatListener
from lib import yt_url, lang_detect, myTTS
from lib.audio_queue import AudioQueueManager
from lib.guildManager import GuildManager
import discord

class VoiceBot:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.guild_manager = GuildManager()
        self.join_locks = {}  # 每個 guild 使用一個 join lock

    async def _get_lock(self, guild_id):
        if guild_id not in self.join_locks:
            self.join_locks[guild_id] = asyncio.Lock()
        return self.join_locks[guild_id]

    async def join(self, ctx):
        """讓機器人加入使用者所在的語音頻道"""
        guild_id = ctx.guild.id
        state = self.guild_manager.get_state(guild_id)
        join_lock = await self._get_lock(guild_id)

        async with join_lock:
            if ctx.author.voice is None:
                return "請先加入語音頻道。"
            user_voice_channel = ctx.author.voice.channel

            if state.voice_client and state.voice_client.is_connected():
                if state.voice_client.channel.id != user_voice_channel.id:
                    await state.voice_client.move_to(user_voice_channel)
                    state.task_channel = state.voice_client.channel
                else:
                    return "已經在語音頻道中。"
            else:
                try:
                    if state.voice_client:
                        await state.voice_client.disconnect(force=True)
                    state.voice_client = await user_voice_channel.connect(reconnect=True, timeout=10)
                    state.task_channel = state.voice_client.channel
                    state.audio_queue = AudioQueueManager(state)  # 每次加入後重新綁定 queue
                except asyncio.TimeoutError:
                    return "連接語音頻道超時，請稍後再試。"
                except discord.ClientException as e:
                    return f"加入語音頻道失敗：{e}"

            return f"已加入語音頻道：{state.voice_client.channel.name}"

    async def leave(self, ctx):
        """讓機器人離開語音頻道"""
        guild_id = ctx.guild.id
        state = self.guild_manager.get_state(guild_id)

        if ctx.voice_client:
            state.task_channel = None
            state.read_mode = False
            await ctx.voice_client.disconnect()
            state.voice_client = None
            return "已離開語音頻道。"
        else:
            return "機器人未在語音頻道中。"

    async def say_yt_chat(self, ctx, url):
        """朗讀 YouTube 聊天室內容"""
        guild_id = ctx.guild.id
        state = self.guild_manager.get_state(guild_id)
        msg = await self.join(ctx)
        await ctx.send(msg, delete_after=3)

        video_id = await yt_url.get_vid(url)
        if video_id is None:
            return "請輸入有效的 YouTube 直播網址。"

        if state.chat_reader and state.chat_reader.chat is not None:
            state.chat_reader.stop() # 停止之前的聊天室讀取
            await ctx.send("已停止之前的聊天室朗讀。", delete_after=3)

        state.chat_reader = ChatListener(video_id, state, state.voice_client.channel)
        asyncio.create_task(state.chat_reader.start(ctx))
        return "開始朗讀聊天室。"

    async def stop_yt_chat(self, ctx):
        """停止朗讀 YouTube 聊天室內容"""
        guild_id = ctx.guild.id
        state = self.guild_manager.get_state(guild_id)
        if state.chat_reader:
            state.chat_reader.stop()  # 停止聊天室讀取
            state.chat_reader = None
            return "已停止朗讀聊天室。"
        else:
            return "無正在朗讀的聊天室"

    async def say(self, ctx, *, text):
        """朗讀指定的文字"""
        guild_id = ctx.guild.id
        state = self.guild_manager.get_state(guild_id)
        msg = await self.join(ctx)
        await ctx.send(msg, delete_after=3)

        if not text:
            return f"請輸入要朗讀的文字。格式：`{ctx.prefix}say <text>`"

        try:
            language = await lang_detect.detect_language_for_gTTS(text)
            audio = await myTTS.get_audio(text, language)
            await state.audio_queue.enqueue(state.voice_client.channel, audio)
            return None
        except Exception as e:
            return f"朗讀錯誤：{e}"

    async def read_out(self, ctx):
        """啟用朗讀模式"""
        guild_id = ctx.guild.id
        state = self.guild_manager.get_state(guild_id)
        msg = await self.join(ctx)
        await ctx.send(msg, delete_after=3)
        state.read_mode = True
        return "🔊 朗讀模式已啟用"

    async def no_read_out(self, ctx):
        """停用朗讀模式"""
        guild_id = ctx.guild.id
        state = self.guild_manager.get_state(guild_id)
        state.read_mode = False
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
            "    - 朗讀 YouTube 聊天室內容",
            f"- `{prefix}stop_yt_chat`",
            "    - 停止朗讀 YouTube 聊天室內容",
            f"- `{prefix}say <文字>`",
            "    - 朗讀指定的文字",
            f"- `{prefix}readout`",
            "    - 啟用朗讀模式 (播報伺服器訊息)",
            f"- `{prefix}noreadout`",
            "    - 停用朗讀模式",
            f"- `{prefix}shutdown`",
            "    - 關閉機器人",
        )
        return help_message
