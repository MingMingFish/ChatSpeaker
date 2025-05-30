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
        if message.author.bot:
            return
        if not message.content.startswith(get_prefix(bot, message)):
            if voice_bot.read_mode:
                audios = [
                    await get_audio(message.author.display_name), # 發言者名稱
                    await get_audio("在", language="zh-TW"),      # 「在」字
                    await get_audio(message.channel.name),        # 頻道名稱
                    await get_audio("說", language="zh-TW"),      # 「說」字
                    await get_audio(message.content)              # 訊息內容
                ]
                task_make_audio = asyncio.create_task(combine_audios(*audios)) # 合併音訊的並行任務
                await voice_bot.audio_queue.enqueue(voice_bot.task_channel, task_make_audio) # 加入全域佇列
            # end if
        await bot.process_commands(message)  # 處理其他指令

    @bot.event
    async def on_voice_state_update(member, before, after):
        if member.bot: # 機器人自己
            if after.channel is None: # 離開語音頻道
                voice_bot.task_channel = None
                voice_bot.voice_client = None
                if voice_bot.chat_reader is not None:
                    voice_bot.chat_reader.stop()
                    voice_bot.chat_reader = None
                if voice_bot.read_mode:
                    voice_bot.read_mode = False
            
            return

        # 判斷活動狀態
        if before.channel != after.channel:
            guild = member.guild
            if after.channel is not None:
                target_channel = after.channel
                activity_message = '加入聊天'
            else:
                target_channel = before.channel
                activity_message = '離開聊天'

            # 合成播報語音
            username = member.display_name
            audios = [
                await get_audio(username),
                await get_audio(activity_message, 'zh-TW')
            ]
            # audio = await combine_audios(*audios)
            task_make_audio = asyncio.create_task(combine_audios(*audios)) # 合併音訊的並行任務
            await voice_bot.audio_queue.enqueue(target_channel, task_make_audio) # 加入全域佇列

