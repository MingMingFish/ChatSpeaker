import asyncio
import discord
from typing import Optional
from lib import chat_listener
from lib import yt_url, lang_detect, myTTS
from lib.audio_queue import AudioQueueManager

class GuildVoiceState:
    """專屬於單一伺服器的狀態封裝（State Container）"""
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.voice_client: Optional[discord.VoiceClient] = None
        self.task_channel: Optional[discord.VoiceChannel] = None
        self.read_mode = False
        self.chat_reader = None
        self.join_lock = asyncio.Lock()  # 每個伺服器獨立的併發鎖
        # 建立時直接綁定自己 (self) 給 Queue Manager
        self.audio_queue = AudioQueueManager(self)

class VoiceBot:
    def __init__(self, bot):
        self.bot = bot
        self.guild_states = {}  # 儲存所有伺服器狀態的 Dictionary
        self.guild_config = getattr(bot, "guild_config", {})

    def get_state(self, guild_id: int) -> GuildVoiceState:
        """取得伺服器專屬狀態，若無則建立一個新的"""
        if guild_id not in self.guild_states:
            self.guild_states[guild_id] = GuildVoiceState(guild_id)
        return self.guild_states[guild_id]

    async def join(self, ctx):
        """讓機器人加入使用者所在的語音頻道"""
        state = self.get_state(ctx.guild.id)

        async with state.join_lock:
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
                        await state.voice_client.disconnect(force=True) # 保險措施：確保沒有殘留連線
                    state.voice_client = await user_voice_channel.connect(reconnect=True, timeout=10)
                    state.task_channel = state.voice_client.channel
                except asyncio.TimeoutError:
                    return "連接語音頻道超時，請稍後再試。"
                except discord.ClientException as e:
                    return f"加入語音頻道失敗：{e}"

            return f"已加入語音頻道：{state.voice_client.channel.name}"

    async def leave(self, ctx):
        """讓機器人離開語音頻道"""
        state = self.get_state(ctx.guild.id)
        
        if state.voice_client:
            # 停止 YouTube 聊天室讀取
            if state.chat_reader is not None:
                state.chat_reader.stop()
                state.chat_reader = None
            
            # 清空佇列與停止播放進程
            state.audio_queue.clear_queue()

            #重置狀態並斷線
            state.task_channel = None
            state.read_mode = False
            await state.voice_client.disconnect()
            state.voice_client = None
            return "已離開語音頻道。"
        else:
            return "機器人未在語音頻道中。"

    async def say_yt_chat(self, ctx, url):
        """朗讀YouTube聊天室內容"""
        state = self.get_state(ctx.guild.id)
        
        msg = await self.join(ctx)  # 確保已加入語音頻道
        await ctx.send(msg, delete_after=3)
        
        # 防呆：如果加入失敗，直接中斷
        if state.voice_client is None:
            return None

        video_id = await yt_url.get_vid(url)
        if video_id is None:
            return "請輸入有效的 YouTube 直播網址。"

        if state.chat_reader and state.chat_reader.chat is not None:
            state.chat_reader.stop() # 停止之前的聊天室讀取
            await ctx.send("已停止之前的聊天室朗讀。", delete_after=3)

        # 初始化 ChatListener 並以非阻塞方式啟動聊天室讀取
        # 把 state 傳給 ChatListener，讓它能夠存取語音連線和其他狀態
        state.chat_reader = chat_listener.ChatListener(video_id, state, state.voice_client.channel)
        asyncio.create_task(state.chat_reader.start(ctx))
        return "開始朗讀聊天室。"

    async def stop_yt_chat(self, ctx):
        """停止朗讀YouTube聊天室內容"""
        state = self.get_state(ctx.guild.id)
        if state.chat_reader is not None:
            state.chat_reader.stop()  # 停止聊天室讀取

            state.chat_reader = None
            return "已停止朗讀聊天室。"
        else:
            return "無正在朗讀的聊天室"

    async def say(self, ctx, *, text):
        """朗讀指定的文字"""
        state = self.get_state(ctx.guild.id)
        
        msg = await self.join(ctx)  # 確保已加入語音頻道
        await ctx.send(msg, delete_after=3)
        
        if state.voice_client is None:
            return None
            
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
        state = self.get_state(ctx.guild.id)
        
        msg = await self.join(ctx)  # 確保已加入語音頻道
        await ctx.send(msg, delete_after=3)
        
        if state.voice_client is None:
            return None
            
        state.read_mode = True
        return "🔊 朗讀模式已啟用"

    async def no_read_out(self, ctx):
        """停用朗讀模式"""
        state = self.get_state(ctx.guild.id)
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