def setup_commands(bot, voice_bot):
    from dotenv import load_dotenv
    from os import getenv
    from discord.ext import commands
    from lib.guild_config import set_prefix
    load_dotenv()
    ADMIN_ID = int(getenv("ADMIN_ID"))

    @bot.command(name="join", help="讓機器人加入使用者所在的語音頻道")
    async def _join(ctx):
        msg = await voice_bot.join(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="leave", help="讓機器人離開語音頻道")
    async def _leave(ctx):
        bot.read_mode = False
        msg = await voice_bot.leave(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="say_yt_chat", help="say_yt_chat <URL> | 朗讀YouTube聊天室內容")
    async def _say_yt_chat(ctx, url):
        msg = await voice_bot.say_yt_chat(ctx, url)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="stop_yt_chat", help="停止朗讀YouTube聊天室內容")
    async def _stop_yt_chat(ctx):
        msg = await voice_bot.stop_yt_chat(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="say", help="say <text> | 朗讀指定的文字")
    async def _say(ctx, *, text):
        msg = await voice_bot.say(ctx, text=text)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="readout", help="啟用朗讀模式")
    async def _read_out(ctx):
        voice_bot.read_mode = True
        msg = await voice_bot.read_out(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="noreadout", help="停用朗讀模式")
    async def _no_read_out(ctx):
        voice_bot.read_mode = False
        msg = await voice_bot.no_read_out(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="helps", help="顯示更多幫助訊息")
    async def _helps(ctx):
        msg = await voice_bot.helps(ctx)
        message = ""
        if msg:
            for line in msg:
                message += line + "\n"
            await ctx.send(message)
        else:
            await ctx.send("Error: 沒有可用的指令。")

    @bot.command(name="set_prefix", help="更改指令前綴符號")
    @commands.has_permissions(administrator=True)
    async def _set_prefix(ctx, new_prefix):
        await set_prefix(voice_bot, ctx.guild.id, new_prefix)
        await ctx.send(f"已將指令前綴設為 `{new_prefix}`")

    @bot.command(name="shutdown", help="將機器人伺服器關機(運營者專用)")
    async def _shutdown(ctx):
        if ctx.author.id != ADMIN_ID:
            await ctx.send("你沒有權限關閉機器人。", delete_after=3)
            return
        await ctx.message.delete()
        await ctx.send("機器人正在關機...", delete_after=3)
        await voice_bot.shutdown(ctx)
