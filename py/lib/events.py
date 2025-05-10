from discord.ext import commands
import discord
import asyncio
from lib.myTTS import get_audio, play_audio_sync, combine_audios
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
                await play_audio_sync(voice_client, audio)
            # end if
        await bot.process_commands(message)  # 處理其他指令

    @bot.event
    async def on_voice_state_update(member, before, after):
        # 排除 bot 自己進出語音的事件
        if member.bot:
            return

        # 偵測加入語音頻道
        if before.channel != after.channel:
            guild = member.guild # 獲取伺服器對象
            if after.channel is not None:
                target_channel = after.channel # 獲取使用者的語音頻道
                activity_message = '加入聊天'
            else:
                target_channel = before.channel # 獲取使用者的語音頻道
                activity_message = '離開聊天'
            # 取得 bot 的 voice client
            bot_voice_client = discord.utils.get(bot.voice_clients, guild=guild)
            original_channel = bot_voice_client.channel if bot_voice_client else None
            # 決定是否要移動/加入語音頻道
            should_disconnect_after = False
            should_return_to_original = False

            while bot_voice_client is not None and bot_voice_client.is_playing():
                await asyncio.sleep(0.1)

            if bot_voice_client is None:
                # bot 沒有連線，加入使用者的語音頻道
                bot_voice_client = await target_channel.connect()
                should_disconnect_after = True
            elif bot_voice_client.channel != target_channel:
                # bot 在其他語音頻道
                await bot_voice_client.move_to(target_channel)
                should_return_to_original = True

            # 播報使用者名稱
            username = member.display_name
            audios = [
                await get_audio(username),
                await get_audio(activity_message, 'zh-TW')
                ]
            audio = await combine_audios(*audios)
            # 播放音訊
            while bot_voice_client is None or not bot_voice_client.is_connected():
                await asyncio.sleep(0.5)
            await play_audio_sync(bot_voice_client, audio)

            while bot_voice_client.is_playing():
                await asyncio.sleep(1)
            # 播報後離開或返回語音頻道
            if should_return_to_original and original_channel:
                await bot_voice_client.move_to(original_channel)
            elif should_disconnect_after:
                await bot_voice_client.disconnect()
