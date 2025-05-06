from discord.ext import commands
import discord
from lib.lang_detect import detect_language_for_gTTS
from lib.bot_audio import play_audio
from lib.myTTS import get_audio

# 調用event函式庫
def setup_events(bot: commands.Bot, voice_bot):
    # 註冊事件處理器
    @bot.event
    async def on_ready():
        print(f"Bot Start Successfully, ID：{bot.user}")
        # print(f"機器人已上線：{bot.user.name}#{bot.user.discriminator}")

    # @bot.event
    # async def on_member_join(member: discord.Member):
    #     channel = discord.utils.get(member.guild.text_channels, name="general")
    #     if channel:
    #         await channel.send(f"歡迎 {member.mention} 加入伺服器！")
    @bot.event
    async def on_message(message):
        if message.author.bot:
            return
        if not message.content.startswith(bot.command_prefix):
            if (
            # if 條件：
                voice_bot.read_mode and
                message.guild and
                message.guild.voice_client and
                message.guild.voice_client.is_connected()):
            # if 內容：
                voice_client = message.guild.voice_client
                # 朗讀發言者名稱
                if message.author.display_name:
                    username = message.author.display_name
                else:
                    username = message.author.name
                language = detect_language_for_gTTS(username)
                audio = get_audio(username, language)
                await play_audio(voice_client, audio)
                # 朗讀「在」字
                audio = get_audio("在", language="zh-TW")
                await play_audio(voice_client, audio)
                # 朗讀頻道名稱
                language = detect_language_for_gTTS(message.channel.name)
                audio = get_audio(message.channel.name, language)
                await play_audio(voice_client, audio)
                # 朗讀「說」字
                audio = get_audio("說", language="zh-TW")
                await play_audio(voice_client, audio)
                # 朗讀訊息內容
                language = detect_language_for_gTTS(message.content)
                audio = get_audio(message.content, language)
                await play_audio(voice_client, audio)
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
            target_channel = after.channel # 獲取使用者的語音頻道

            # 取得 bot 的 voice client
            bot_voice_client = discord.utils.get(bot.voice_clients, guild=guild)
            original_channel = bot_voice_client.channel if bot_voice_client else None

            # 決定是否要移動/加入語音頻道
            should_disconnect_after = False
            should_return_to_original = False

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
            language = detect_language_for_gTTS(username)
            audio = get_audio(username, language)
            await play_audio(bot_voice_client, audio)
            audio = get_audio('加入聊天', 'zh-TW')
            await play_audio(bot_voice_client, audio)

            # 播報後處理離開或返回語音頻道
            if should_return_to_original and original_channel:
                await bot_voice_client.move_to(original_channel)
            elif should_disconnect_after:
                await bot_voice_client.disconnect()
