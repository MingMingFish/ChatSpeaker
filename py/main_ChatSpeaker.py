import os
from dotenv import load_dotenv
import logging
import discord
from discord.ext import commands
from lib.voice_bot import VoiceBot
from lib.myCommands import setup_commands

# 降低語音播報player的日誌提示級別，僅顯示錯誤和警告
logging.getLogger("discord.player").setLevel(logging.WARNING)

# 載入環境變數
load_dotenv()
TOKEN = os.getenv("DC_BOT_TOKEN")
prefix = ">"  # 指令前綴符號
# Bot基礎設定
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
# 建立語音Bot實例
bot = commands.Bot(command_prefix=prefix, intents=intents)
voice_bot = VoiceBot(bot)
setup_commands(bot, voice_bot)  # 傳入 myCommands.py

# 調用event函式庫
@bot.event
async def on_ready():
    print(f"Bot Start Successfully, ID：{bot.user}")


if __name__ == "__main__":
    bot.run(TOKEN)
