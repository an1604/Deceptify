from telethon import TelegramClient, events
import asyncio
from app.Server.LLM.llm import llm_factory


class telegram_client(object):
    def __init__(self, api_id, api_hash, phone_number, profile_name, attack_purpose,
                 telegram_target):
        """
        This telegram client class can log in for a specific user and send messages to mimic
         such as voice records, regular messages, etc.
        :param api_id: Telegram API ID
        Parameters
        ----------
        api_id - Your Telegram API ID
        api_hash - Your Telegram API hash
        phone_number - Your Telegram phone number
        profile_name - Your profile name (Deceptify client)
        attack_purpose - Attack purpose (Deceptify client)
        telegram_target - The target receiver
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.telegram_target = telegram_target
        self.profile_name = profile_name
        self.attack_purpose = attack_purpose
        self.llm = llm_factory.generate_new_attack(attack_purpose, profile_name)

        self.received_response = asyncio.Event()
        self.current_message = None
        self.stop = False

        self.client = TelegramClient(f'session-{self.profile_name}', api_id, api_hash)
        self.handle_routes(self.client)
        self.run_client()

    async def send_message(self):
        # while not self.stop:
        #     await self.received_response.wait()
        #     self.received_response.clear()
        message = await asyncio.to_thread(self.handle_message, self.current_message)
        await self.client.send_message(self.telegram_target, message)

    def handle_message(self, msg):
        flag = False  # This flag will represent the client's acceptation
        # to send the following response to the target, the clients have the opportunity to
        # regenerate the answer if they want to, to ensure that the attack is accurate.

        answer = None
        while not flag:
            answer, flag = self.llm.get_answer(msg), True
        return answer

    def handle_routes(self, client):
        @client.on(events.NewMessage)
        async def handle_new_message(event):
            if event.is_private:
                self.current_message = event.message.text
                # self.received_response.set()
                message = await asyncio.to_thread(self.handle_message, self.current_message)
                await self.client.send_message(self.telegram_target, message)
                self.current_message = None

    async def run_client(self):
        await self.client.start(phone=self.phone_number)
        await asyncio.gather(
            self.send_message(),  # Sending messages
            self.client.run_until_disconnected()  # Receiving messages
        )
        with self.client:
            self.client.loop.run_until_complete(self.run_client())
