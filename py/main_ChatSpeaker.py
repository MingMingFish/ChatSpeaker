import os
from dotenv import load_dotenv
import logging
import discord
from discord.ext import commands
from lib.voiceBot import VoiceBot
from lib.myCommands import setup_commands
from lib.events import setup_events
from lib.guild_config import get_prefix, load_config

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
config = load_config()  # 注意：這要在 bot 初始化之前做
# 建立語音Bot實例
bot = commands.Bot(command_prefix=lambda bot, msg: get_prefix(bot, msg), intents=intents)
bot.guild_config = config  # 初始化後掛載設定資料
voice_bot = VoiceBot(bot)
setup_commands(bot, voice_bot)  # 設定commands  : myCommands.py
setup_events(bot, voice_bot)    # 調用事件處理器 : event.py

if __name__ == "__main__":
    bot.run(TOKEN)
