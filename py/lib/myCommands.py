def setup_commands(bot, voice_bot):

    @bot.command()
    async def join(ctx):
        msg = await voice_bot.join(ctx)
        if msg:
            await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()

    @bot.command()
    async def leave(ctx):
        bot.read_mode = False  # 停用朗讀模式
        msg = await voice_bot.leave(ctx)
        if msg:
            await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()

    @bot.command()
    async def say_yt_chat(ctx, url):
        msg = await voice_bot.say_yt_chat(ctx, url)
        if msg:
            await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()

    @bot.command()
    async def stop_yt_chat(ctx):
        msg = await voice_bot.stop_yt_chat(ctx)
        if msg:
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
        if msg:
            await ctx.send(msg, delete_after = 3)
        await ctx.message.delete()


    @bot.command()
    async def noreadout(ctx):
        voice_bot.read_mode = False
        msg = await voice_bot.noreadout(ctx)
        if msg:
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

    