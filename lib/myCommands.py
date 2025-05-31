def setup_commands(bot, voice_bot):
    from dotenv import load_dotenv
    from os import getenv
    from discord.ext import commands
    from lib.guild_config import set_prefix, get_prefix
    load_dotenv()
    ADMIN_ID = int(getenv("ADMIN_ID"))

    @bot.command(name="join", help="Join the voice chat")
    async def _join(ctx):
        msg = await voice_bot.join(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="leave", help="leave the voice chat")
    async def _leave(ctx):
        bot.read_mode = False
        msg = await voice_bot.leave(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="say_yt_chat", help="say_yt_chat <URL> | Read YouTube chat commends")
    async def _say_yt_chat(ctx, url):
        msg = await voice_bot.say_yt_chat(ctx, url)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="stop_yt_chat", help="Stop reading YouTube chat")
    async def _stop_yt_chat(ctx):
        msg = await voice_bot.stop_yt_chat(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="say", help="say <text> | Say the words")
    async def _say(ctx, *, text=''):
        if not text:
            msg = f"請輸入要朗讀的文字。格式：`{get_prefix(voice_bot, ctx)}say <text>`"
        else:
            msg = await voice_bot.say(ctx, text=text)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="readout", help="Start read-out mode, says the chat in the Discord Server")
    async def _read_out(ctx):
        voice_bot.read_mode = True
        msg = await voice_bot.read_out(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="noreadout", help="Stop read-out mode")
    async def _no_read_out(ctx):
        voice_bot.read_mode = False
        msg = await voice_bot.no_read_out(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="helps", help="Shows more helps info.")
    async def _helps(ctx):
        prefix = get_prefix(voice_bot, ctx)
        msg = await voice_bot.helps(ctx, prefix=prefix)
        message = ""
        if msg:
            for line in msg:
                message += line + "\n"
            await ctx.send(message)
            await ctx.message.delete()
        else:
            await ctx.send("Error: 沒有可用的指令。")

    @bot.command(name="set_prefix", help="Change the prefix")
    @commands.has_permissions(administrator=True)
    async def _set_prefix(ctx, new_prefix):
        await set_prefix(voice_bot, ctx.guild.id, new_prefix)
        await ctx.send(f"已將指令前綴設為 `{new_prefix}`")

    @bot.command(name="shutdown", help="Shutdown the bot. (Bot owner only)")
    async def _shutdown(ctx):
        if ctx.author.id != ADMIN_ID:
            await ctx.send("你沒有權限關閉機器人。", delete_after=3)
            return
        await ctx.message.delete()
        await ctx.send("機器人正在關機...", delete_after=3)
        await voice_bot.shutdown(ctx)
