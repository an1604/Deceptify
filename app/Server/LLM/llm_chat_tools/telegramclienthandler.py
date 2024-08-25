import asyncio
import os
from telethon import TelegramClient, events, errors
from dotenv import load_dotenv
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
import qrcode
from PIL import Image
from app.Server.data.fs import FilesManager

load_dotenv()


class TelegramInfo(object):
    def __init__(self, app_id, app_hash, profile_name, phone_number, qr_path):
        self.app_id = app_id
        self.qr_path = qr_path
        self.app_hash = app_hash
        self.profile_name = profile_name
        self.phone_number = phone_number
        self.authentication_code = None
        self.is_connected = False

    def set_authentication_code(self, authentication_code):
        self.authentication_code = authentication_code


class TelegramClientHandler(object):
    def __init__(self, app_id, app_hash, phone_number, auth_event, qr_path):
        self.app_id = app_id
        self.app_hash = app_hash
        self.phone_number = phone_number
        self.auth_event = auth_event
        self.qr_path = qr_path

        self.qr_login = None
        self.auth_code = None

        self.messages_received = []
        self.loop = None
        self.make_event_loop()

        self.client = TelegramClient(StringSession(), self.app_id, self.app_hash)
        self.initialize_client()

    def handle_routes(self, client):
        print(f"handle_routes called with client {client}")

        @client.on(events.NewMessage)
        async def handle_new_message(event):
            message = event.message.message
            print(f'New message received: {message}')
            self.messages_received.append(message)

    def initialize_client(self):
        self.handle_routes(self.client)
        # self.loop.run_until_complete(self.connect())  # Do not move on to the next instruction
        # until the client connects and authorizes.

        self.loop.create_task(self.run_client())  # Run the telegram client as a background task
        print("Added run_client to the loop")

    async def run_client(self):
        try:
            await self.client.start(phone=self.phone_number)
            print('Client is running...')
            await self.client.run_until_disconnected()
        except errors.AuthKeyUnregisteredError:
            print("Authorization key not found or invalid. Re-authenticating...")
            await self.authenticate_client_via_msg()
            await self.run_client()  # Retry running the client after re-authentication
        except Exception as e:
            print(f"An error occurred: {e}")
            await self.run_client()

    async def send_message(self, receiver, message):
        try:
            await self.client.connect()
            self.handle_routes(self.client)

            await self.client.send_message(receiver, message)

            print(f'Message sent: {message}')
        except errors.AuthKeyUnregisteredError:
            print("Authorization key not found or invalid. Re-authenticating...")
            # await self.authenticate_client_via_msg()
            await self.send_message(receiver, message)  # Retry sending the message after re-authentication

    async def send_audio(self, receiver, audiofile_path):
        try:
            await self.client.connect()
            self.handle_routes(self.client)
            if await self.client.is_user_authorized():
                if audiofile_path and os.path.exists(audiofile_path):
                    print("Audio file found!")
                    await self.client.send_file(receiver, audiofile_path)
                else:
                    print(f"Audio file {audiofile_path} does not exist.")
        except errors.AuthKeyUnregisteredError:
            print("Authorization key not found or invalid. Re-authenticating...")
            await self.authenticate_client_via_qr()
            await self.send_audio(receiver, audiofile_path)  # Retry sending the audio after re-authentication

    def get_messages(self):
        return self.messages_received

    def make_event_loop(self):
        try:
            self.loop = asyncio.get_event_loop()
            asyncio.set_event_loop(self.loop)
        except RuntimeError as e:
            if str(e).startswith('There is no current event loop in thread'):
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
            else:
                raise

    async def stop_client(self):
        if self.loop:
            self.loop.close()
            self.loop = None
        self.client.disconnect()
        print('Client disconnected')

    async def authenticate_client_via_qr(self):
        self.qr_login = await self.client.qr_login()
        display_url_as_qr(self.qr_login.url, self.qr_path)
        await self.qr_login.wait()

    async def authenticate_client_via_msg(self, counter=None):
        print("Inside authenticate_client_via_msg")

        await self.client.connect()

        if counter is None or counter <= 1:
            # self.auth_event.set()  # Set the event to alert to the background thread that authentication needed.
            await self.client.send_code_request(self.phone_number)
            self.auth_code = input('Enter the code you received: ')
            # self.auth_event.wait()
            try:
                await self.client.sign_in(self.phone_number, self.auth_code)
            except SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Please enter your password: ')
                await self.client.sign_in(password=password)
        else:
            print(f"Waiting for the client to send the authentication code... (Attempt {counter})")

    async def sign_in(self, code):
        await self.client.sign_in(self.phone_number, code)

    async def connect(self):
        print("connect() function called")
        tried_to_connect = False  # Flag that checks if we already tried to connect
        counter_of_tries = 0  # Counter for authentication code

        while not self.client.is_connected():
            try:
                await self.client.connect()
                if not await self.client.is_user_authorized():
                    counter_of_tries += 1
                    if tried_to_connect:
                        print("Connection attempt failed")
                        await self.authenticate_client_via_msg(counter_of_tries)
                        tried_to_connect = False
                else:
                    print("Client successfully connected and authorized.")
                    break  # Exit the loop if connected and authorized
            except Exception as e:
                print(f"Connection error: {e}")
                await asyncio.sleep(2)  # Wait before retrying


def display_url_as_qr(url, save_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(save_path)
    return save_path
