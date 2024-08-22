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
    def __init__(self, app_id, app_hash, profile_name, phone_number,
                 attack_purpose=None, telegram_target=None, send_audio=True):
        self.app_id = app_id
        self.app_hash = app_hash
        self.phone_number = phone_number
        self.telegram_target = telegram_target
        self.profile_name = profile_name
        self.attack_purpose = attack_purpose
        self.send_record = send_audio
        self.llm = llm_factory.generate_new_attack(attack_purpose, profile_name)

        self.is_first_msg = True
        self.messages_received = []

        self.is_initialized = False
        self.updates_event = None
        self.initialized_thread = None

        self.audio_path = None

        self.client = TelegramClient(f'session-{self.profile_name}', app_id, app_hash)
        self.handle_routes(self.client)
        self.run_client_thread = Thread(target=self.run)
        self.loop = asyncio.new_event_loop()

    def need_to_send_record(self):
        if self.is_first_msg and self.send_record:
            self.is_first_msg = False
            return True
        return False

    def set_audio_path(self, audio_path):
        self.audio_path = audio_path

    def set_advanced_params(self, target_name, attack_purpose, clone_voice_for_record):
        self.telegram_target = target_name
        self.attack_purpose = attack_purpose
        self.send_record = clone_voice_for_record

    async def send_message(self, message):
        await self.client.send_message(self.telegram_target, message)

    async def send_audio(self):
        """Send an audio file to the target."""
        print(f'Sending audio file to {self.telegram_target}')
        await self.client.connect()
        print("Client connected")
        # while not await self.client.is_user_authorized():
        if await self.client.is_user_authorized():
            if os.path.exists(self.audio_path):
                print("Audio file found!")
                await self.client.send_file(self.telegram_target, self.audio_path)
                # os.remove(audiofile_path)
                print("Audio file deleted!")
            else:
                print(f"Audio file {self.audio_path} does not exist.")

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
                if self.updates_event:
                    self.updates_event.set()
                    self.messages_received.append(incoming_message)

    async def run_client(self):
        await self.client.start(phone=self.phone_number)
        await asyncio.gather(
            # self.send_message(), # Sending text messagges
            self.send_audio(),  # Sending audio records
            self.client.run_until_disconnected()  # Receiving messages
        )

    def run(self):
        # This method runs the asyncio event loop to start the client and handle additional tasks
        with self.client:
            self.client.loop.run_until_complete(self.run_client())

    async def stop_client(self):
        await self.client.disconnect()
        # self.run_client_thread.join()
        self.loop.stop()
        self.initialized_thread.join(1)

    def run_telegram_client(self, update_event):
        if not self.is_initialized:
            self.updates_event = update_event
            self.is_initialized = True
            self.initialized_thread = Thread(target=self.run)
            self.initialized_thread.start()
        return self.initialized_thread


async def send_record(telegram_client, audio_filepath=None):
    if audio_filepath:
        telegram_client.set_audio_path(audio_filepath)
    await asyncio.to_thread(telegram_client.send_audio)


async def send_message(telegram_client, message):
    await asyncio.to_thread(telegram_client.send_message, message)


# if __name__ == '__main__':
#     telegram_client = TelegramClientHandler(
#         app_id=default_app_id,
#         app_hash=default_app_hash,
#         phone_number='+972522464648',
#         telegram_target='+972523943201',
#         attack_purpose='Bank',
#         profile_name='Default'
#     )
#
#     print("line 106")
#     send_record(telegram_client)
#     print("line 108")
#
#     telegram_client.run()

