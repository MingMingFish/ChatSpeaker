import asyncio
import pytchat
from lib.myTTS import get_audio, combine_audios
from lib.audio_queue import audio_queue
from httpx import LocalProtocolError

class ChatListener:
    def __init__(self, video_id, voice_bot, bot_voice_channel):
        self.video_id = video_id
        self.voice_bot = voice_bot
        self.bot_voice_channel = bot_voice_channel
        self.continue_flag = True
        self.chat = None # 尚未建立聊天室實例

    async def start(self, ctx):
        """開始聊天室讀取"""
        self.chat = pytchat.create(self.video_id, interruptable=False)
        self.continue_flag = True
        while self.continue_flag:
            while self.chat.is_alive():
                chat_data = self.chat.get()
                if chat_data and chat_data.items:
                    await self.process_chat_data(chat_data)
                await asyncio.sleep(3)  # 防止過多請求造成負擔
            try:
                self.chat.raise_for_status()
            except LocalProtocolError as error:
                print(f"httpx.LocalProtocolError: {error}")
                print("Reconnecting Live Chat...")
                self.chat.terminate()
                self.continue_flag = True
            except pytchat.exceptions.NoContents as error:
                # print(f"pytchat.exceptions.NoContents: {error}")
                # print("Live stream has ended.")
                await ctx.send("Live stream has ended.", delete_after=60)
                self.chat.terminate()
                self.continue_flag = False
                break
            except Exception as error:
                print(f"Error: {error}")
                self.continue_flag = False
                break
        self.chat.terminate()
        self.voice_bot.chat_reader = None
        print("Chat reader has ended.")

    def stop(self):
        """停止聊天室讀取"""
        self.continue_flag = False
        if self.chat.is_alive():
            self.chat.terminate()

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
        # 語音加入佇列等待播放
        task_make_audio = asyncio.create_task(combine_audios(*audios)) # 合併音訊的並行任務
        await audio_queue.enqueue(self.bot_voice_channel, task_make_audio) # 加入全域佇列
