import asyncio
import pytchat
from lib.myTTS import get_audio, combine_audios, play_audio_sync

class ChatListener:
    def __init__(self, video_id, voice_bot, bot_voice_channel):
        self.video_id = video_id
        self.chat = pytchat.create(video_id, interruptable=False)
        self.voice_bot = voice_bot
        self.bot_voice_channel = bot_voice_channel
        self.stop_flag = False

    async def start(self):
        """開始聊天室讀取"""
        while not self.stop_flag:
            if self.chat.is_alive():
                chat_data = self.chat.get()
                if chat_data and chat_data.items:
                    await self.process_chat_data(chat_data)
            else:
                print("Chat data finished.")
                break
            await asyncio.sleep(3)  # 防止過多請求造成負擔

    def stop(self):
        """停止聊天室讀取"""
        self.stop_flag = True

    async def process_chat_data(self, chat_data):
        """處理聊天室訊息"""
        for message in chat_data.items:
            print(f'{message.datetime}| [{message.author.name}]說: {message.message}')
            await self.play_message(message)

    async def play_message(self, message):
        """處理訊息並進行語音播放"""
        # 語音生成
        audios = [
            await get_audio(message.author.name), # 名字
            await get_audio("說", language='zh-TW'), # "說"字
            await get_audio(message.message), # 訊息
        ]
        # 語音合成
        audio = await combine_audios(*audios)
        # 播放語音
        await play_audio_sync(self.bot_voice_channel, audio)
