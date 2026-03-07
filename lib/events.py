from discord.ext import commands
import discord
import asyncio
from lib.myTTS import get_audio, combine_audios
from lib.guild_config import get_prefix

# 調用event函式庫
def setup_events(bot: commands.Bot, voice_bot):
    # 註冊事件處理器
    @bot.event
    async def on_ready():
        print(f"Bot Start Successfully, ID：{bot.user}")

    @bot.event
    async def on_member_join(member: discord.Member):
        channel = discord.utils.get(member.guild.text_channels, name="大門")
        if channel:
            await channel.send(f"{member.mention} 歡迎光臨盈月酒館！")

    @bot.event
    async def on_message(message):
        # 排除機器人發言與私訊 (私訊沒有 guild 屬性)
        if message.author.bot or message.guild is None:
            return

        # 取得該伺服器的專屬狀態
        state = voice_bot.get_state(message.guild.id)

        if not message.content.startswith(get_prefix(bot, message)):
            if state.read_mode: # 改看 state 的狀態
                try:
                    audios = [
                        await get_audio(message.author.display_name), # 發言者名稱
                        await get_audio("在", language="zh-TW"),      # 「在」字
                        await get_audio(message.channel.name),        # 頻道名稱
                        await get_audio("說", language="zh-TW"),      # 「說」字
                        await get_audio(message.content)              # 訊息內容
                    ]
                    task_make_audio = asyncio.create_task(combine_audios(*audios))
                    await state.audio_queue.enqueue(state.task_channel, task_make_audio) 
                except AssertionError as e:
                    print(f"[Read-out]: 無效的語音文字 - {e}")
                    pass # 略過這則無法朗讀的訊息
        
        await bot.process_commands(message)

    @bot.event
    async def on_voice_state_update(member, before, after):
        if member.guild is None:
            return
            
        # 取得該伺服器的專屬狀態
        state = voice_bot.get_state(member.guild.id)

        # 判斷是否為「任何機器人」的動作
        if member.bot: 
            # 只有當「本機器人自己」離開時，才清空狀態
            if member.id == bot.user.id and after.channel is None: 
                state.task_channel = None
                state.voice_client = None
                if state.chat_reader is not None:
                    state.chat_reader.stop()
                    state.chat_reader = None
                if state.read_mode:
                    state.read_mode = False
            return # 其他機器人的進出不播報，直接返回

        # 判斷一般使用者的活動狀態
        if before.channel != after.channel:
            if after.channel is not None:
                target_channel = after.channel
                activity_message = '加入聊天'
            else:
                target_channel = before.channel
                activity_message = '離開聊天'

            # 合成播報語音
            username = member.display_name
            try:
                audios = [
                    await get_audio(username),
                    await get_audio(activity_message, 'zh-TW')
                ]
                task_make_audio = asyncio.create_task(combine_audios(*audios)) # 合併音訊的並行任務
                await state.audio_queue.enqueue(target_channel, task_make_audio) # 加入佇列
            except AssertionError as e:
                print(f"[Voice-State]: {e}")
                pass
