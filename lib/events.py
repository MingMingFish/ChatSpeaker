from discord.ext import commands
import discord
import asyncio
from lib.myTTS import get_audio, enqueue_audio, combine_audios
from lib.guild_config import get_prefix
from lib.audio_queue import audio_queue

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
            if (
            # if 條件：
                voice_bot.read_mode and
                message.guild and
                message.guild.voice_client and
                message.guild.voice_client.is_connected()):
            # if 內容：
                voice_client = message.guild.voice_client
                audios = [
                    await get_audio(message.author.display_name), # 發言者名稱
                    await get_audio("在", language="zh-TW"),      # 「在」字
                    await get_audio(message.channel.name),        # 頻道名稱
                    await get_audio("說", language="zh-TW"),      # 「說」字
                    await get_audio(message.content)              # 訊息內容
                ]
                audio = await combine_audios(*audios)  # 合併音訊
                await enqueue_audio(voice_client, audio)
            # end if
        await bot.process_commands(message)  # 處理其他指令

    @bot.event
    async def on_voice_state_update(member, before, after):
        if member.bot: # 機器人自己
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
            audio_path = await combine_audios(*audios)

            # 加入全域佇列：由 queue 負責播放、移動、回原任務頻道
            await audio_queue.enqueue(target_channel, audio_path)

