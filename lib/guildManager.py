import asyncio
import discord
from lib.chat_listener import ChatListener

class GuildBotState:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.voice_client: discord.VoiceClient | None = None
        self.read_mode: bool = False
        self.chat_reader: ChatListener | None = None
        self.task_channel: discord.VoiceChannel | None = None
        self.audio_queue: asyncio.Queue = asyncio.Queue()

class GuildManager:
    def __init__(self):
        self.guild_states: dict[int, GuildBotState] = {}

    def get(self, guild_id: int) -> GuildBotState | None:
        return self.guild_states.get(guild_id)

    def set(self, guild_id: int, state: GuildBotState):
        self.guild_states[guild_id] = state

    def remove(self, guild_id: int):
        self.guild_states.pop(guild_id, None)

    def all(self) -> list[GuildBotState]:
        return list(self.guild_states.values())

    def get_state(self, guild_id: int) -> GuildBotState:
        """🆕 若 guild_id 尚未註冊狀態，則建立並回傳"""
        if guild_id not in self.guild_states:
            state = GuildBotState(guild_id)
            self.guild_states[guild_id] = state
        return self.guild_states[guild_id]

    def create_chat_listener(self, guild_id: int) -> ChatListener:
        """🆕 建立 ChatListener 並儲存"""
        state = self.get_state(guild_id)
        listener = ChatListener(guild_id, self)
        state.chat_reader = listener
        return listener
