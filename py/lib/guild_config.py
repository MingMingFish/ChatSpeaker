import json
import os

CONFIG_PATH = "sever_config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

async def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_prefix(bot, message):
    if message.guild is None:
        return ">"  # default prefix for DM
    guild_id = str(message.guild.id)
    return bot.guild_config.get(guild_id, {}).get("prefix", ">")

async def set_prefix(voice_bot, guild_id, new_prefix):
    guild_id = str(guild_id)
    config = voice_bot.bot.guild_config
    if guild_id not in config:
        config[guild_id] = {}
    config[guild_id]["prefix"] = new_prefix
    await save_config(config)