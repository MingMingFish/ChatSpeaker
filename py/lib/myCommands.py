from lib.myTTS import detect_language_for_gTTS, get_audio
from lib.bot_audio import play_audio

def setup_commands(bot, voice_bot):

    @bot.command()
    async def join(ctx):
        msg = await voice_bot.join(ctx)
        await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()

    @bot.command()
    async def leave(ctx):
        bot.read_mode = False  # 停用朗讀模式
        msg = await voice_bot.leave(ctx)
        await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()

    @bot.command()
    async def say_yt_chat(ctx, url):
        msg = await voice_bot.say_yt_chat(ctx, url)
        await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()

    @bot.command()
    async def stop_yt_chat(ctx):
        msg = await voice_bot.stop_yt_chat()
        await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()

    @bot.command()
    async def say(ctx, *, text):
        msg = await voice_bot.say(ctx, text=text)
        if msg:
            await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()
        

    @bot.command()
    async def readout(ctx):
        voice_bot.read_mode = True
        msg = await voice_bot.readout(ctx)
        await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()


    @bot.command()
    async def noreadout(ctx):
        voice_bot.read_mode = False
        msg = voice_bot.noreadout()
        await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()
    
    @bot.command()
    async def shutdown(ctx):
        if ctx.author.id != 325213129405628417:
            await ctx.send("你沒有權限關閉機器人。", delete_after = 3)
        await ctx.message.delete()
        await ctx.send("機器人正在關機...", delete_after = 3)
        await voice_bot.shutdown(ctx)

    @bot.command()
    async def helps(ctx):
        msg = await voice_bot.helps(ctx)
        message = ""
        if msg:
            for line in msg:
                message += line + "\n"
            await ctx.send(message)
        else:
            await ctx.send("Error: 沒有可用的指令。")

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