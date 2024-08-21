import os
import time
from threading import Thread

from telethon import TelegramClient, events
import asyncio
from app.Server.LLM.llm import llm_factory
from dotenv import load_dotenv

load_dotenv()
default_app_id = os.getenv('TELEGRAM_CLIENT_APP_ID')
default_app_hash = os.getenv('TELEGRAM_CLIENT_APP_HASH')


class TelegramClientHandler(object):
    def __init__(self, app_id, app_hash, profile_name, phone_number, attack_purpose=None, telegram_target=None,
                 send_audio=True):
        self.app_id = app_id
        self.app_hash = app_hash
        self.phone_number = phone_number
        self.telegram_target = telegram_target
        self.profile_name = profile_name
        self.attack_purpose = attack_purpose
        self.send_record = send_audio
        # self.llm = llm_factory.generate_new_attack(attack_purpose, profile_name)

        self.client = TelegramClient(f'session-{self.profile_name}', app_id, app_hash)
        self.handle_routes(self.client)
        self.run_client_thread = Thread(target=self.run)
        self.loop = asyncio.new_event_loop()

    async def send_message(self, message):
        response_message = await asyncio.to_thread(self.handle_message, message)
        await self.client.send_message(self.telegram_target, response_message)

    async def send_audio(self, audiofile_path):
        """Send an audio file to the target."""
        await self.client.connect()
        while not await self.client.is_user_authorized():
            if await self.client.is_user_authorized():
                if os.path.exists(audiofile_path):
                    print("Audio file found!")
                    await self.client.send_file(self.telegram_target, audiofile_path)
                    # os.remove(audiofile_path)
                    print("Audio file deleted!")
                else:
                    print(f"Audio file {audiofile_path} does not exist.")

    def handle_message(self, msg):
        flag = False
        answer = None
        while not flag:
            answer, flag = self.llm.get_answer(msg), True
        return answer

    def handle_routes(self, client):
        @client.on(events.NewMessage)
        async def handle_new_message(event):
            if event.is_private:
                incoming_message = event.message.text
                print(incoming_message)
                # response_message = await asyncio.to_thread(self.handle_message, incoming_message)
                # await self.client.send_message(self.telegram_target, response_message)
                await self.client.send_message(self.telegram_target, "חמי הקטלני")

    async def run_client(self):
        await self.client.start(phone=self.phone_number)
        await self.client.run_until_disconnected()

    def run(self):
        # This method runs the asyncio event loop to start the client and handle additional tasks
        with self.client:
            try:
                self.loop = asyncio.get_event_loop()
                print("Client run...")
                self.loop.run_until_complete(self.run_client())
            except RuntimeError as e:
                if str(e).startswith('There is no current event loop in thread'):
                    self.loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(self.loop)
                    self.loop.run_until_complete(self.run_client())
                else:
                    raise

    async def stop_client(self):
        await self.client.disconnect()
        # self.run_client_thread.join()
        self.loop.stop()


if __name__ == '__main__':
    telegram_client = TelegramClientHandler(
        app_id=default_app_id,
        app_hash=default_app_hash,
        phone_number='+972522464648',
        telegram_target='+972523943201',
        attack_purpose='Bank',
        profile_name='Default'
    )

    audio_path = r"C:\Users\adina\Desktop\WhatsApp Audio 2024-08-19 at 16.28.59.mp3"
    asyncio.to_thread(telegram_client.send_audio, audio_path)

    telegram_client.run()

    # telegram_client.send_audio(audio_path)
