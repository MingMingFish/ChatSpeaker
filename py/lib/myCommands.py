def setup_commands(bot, voice_bot):
    from dotenv import load_dotenv
    from os import getenv
    from discord.ext import commands
    from lib.guild_config import set_prefix
    load_dotenv()
    ADMIN_ID = int(getenv("ADMIN_ID"))

    @bot.command(name="join")
    async def _join(ctx):
        msg = await voice_bot.join(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="leave")
    async def _leave(ctx):
        bot.read_mode = False
        msg = await voice_bot.leave(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="say_yt_chat")
    async def _say_yt_chat(ctx, url):
        msg = await voice_bot.say_yt_chat(ctx, url)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="stop_yt_chat")
    async def _stop_yt_chat(ctx):
        msg = await voice_bot.stop_yt_chat(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="say")
    async def _say(ctx, *, text):
        msg = await voice_bot.say(ctx, text=text)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="readout")
    async def _read_out(ctx):
        voice_bot.read_mode = True
        msg = await voice_bot.read_out(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="noreadout")
    async def _no_read_out(ctx):
        voice_bot.read_mode = False
        msg = await voice_bot.no_read_out(ctx)
        if msg:
            await ctx.send(msg, delete_after=3)
        await ctx.message.delete()

    @bot.command(name="helps")
    async def _helps(ctx):
        msg = await voice_bot.helps(ctx)
        message = ""
        if msg:
            for line in msg:
                message += line + "\n"
            await ctx.send(message)
        else:
            await ctx.send("Error: 沒有可用的指令。")

    @bot.command(name="set_prefix")
    @commands.has_permissions(administrator=True)
    async def _set_prefix(ctx, new_prefix):
        set_prefix(voice_bot, ctx.guild.id, new_prefix)
        await ctx.send(f"已將指令前綴設為 `{new_prefix}`")

    @bot.command(name="shutdown")
    async def _shutdown(ctx):
        if ctx.author.id != ADMIN_ID:
            await ctx.send("你沒有權限關閉機器人。", delete_after=3)
            return
        await ctx.message.delete()
        await ctx.send("機器人正在關機...", delete_after=3)
        await voice_bot.shutdown(ctx)
