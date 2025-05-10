import json
import os

CONFIG_FILE = "lib/guild_config.json"
DEFAULT_PREFIX = ">"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def get_prefix(bot, message):
    guild_id = str(message.guild.id) if message.guild else None
    if guild_id and guild_id in bot.guild_config:
        return bot.guild_config[guild_id].get("prefix", DEFAULT_PREFIX)
    return DEFAULT_PREFIX

def set_prefix(bot, guild_id, new_prefix):
    guild_id = str(guild_id)
    if guild_id not in bot.guild_config:
        bot.guild_config[guild_id] = {}
    bot.guild_config[guild_id]["prefix"] = new_prefix
    save_config(bot.guild_config)
