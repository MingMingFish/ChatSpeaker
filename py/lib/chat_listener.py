
import asyncio
import pytchat
from lib import bot_audio, myTTS

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
        # 假設 myTTS 和 bot_audio 是已經定義好的語音處理工具
        lang1 = myTTS.detect_language_for_gTTS(message.author.name)
        audio1 = myTTS.get_audio(message.author.name, lang1)
        await bot_audio.play_audio(self.bot_voice_channel, audio1)

        # 播放語音 "說"
        audio2 = myTTS.get_audio("說", language='zh-TW')
        await bot_audio.play_audio(self.bot_voice_channel, audio2)

        # 播放訊息內容語音
        lang3 = myTTS.detect_language_for_gTTS(message.message)
        audio3 = myTTS.get_audio(message.message, lang3)
        await bot_audio.play_audio(self.bot_voice_channel, audio3)
