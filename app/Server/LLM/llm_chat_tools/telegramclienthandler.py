import asyncio
import os
import logging
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from telethon import functions, types

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TelegramInfo(object):
    def __init__(self, app_id, app_hash, profile_name, phone_number, qr_path):
        self.app_id = app_id
        self.qr_path = qr_path
        self.app_hash = app_hash
        self.profile_name = profile_name
        self.phone_number = phone_number


class TelegramClientHandler(object):
    def __init__(self, app_id, app_hash, phone_number, auth_event, qr_path):
        self.app_id = app_id
        self.app_hash = app_hash
        self.phone_number = phone_number
        self.auth_event = auth_event
        self.qr_path = qr_path

        self.qr_login = None
        self.phone_hash = None
        self.auth_code = None

        self.messages_received = []
        self.loop = None

        self.client = None
        self.loop = None
        self.initialize_client()

    def handle_routes(self, client):
        logging.info(f"handle_routes called with client {client}")

        @client.on(events.NewMessage)
        async def handle_new_message(event):
            message = event.message.message
            logging.info(f'New message received: {message}')
            self.messages_received.append(message)

    def initialize_client(self, needs_flush=False):
        if needs_flush:
            self.flush()

        self.make_event_loop()
        self.client = TelegramClient(StringSession(), self.app_id, self.app_hash)

        self.handle_routes(self.client)
        self.loop.create_task(self.run_client())  # Run the telegram client as a background task
        logging.info("Added run_client to the loop")

    async def run_client(self):
        """Run the Telegram client until it is disconnected or an error occurs."""
        retry_count = 0
        max_retries = 5

        while retry_count < max_retries:
            try:
                await self.client.start(phone=self.phone_number)
                logging.info('Client is running...')
                await self.client.run_until_disconnected()
                break  # Exit loop if client disconnects normally

            except errors.AuthKeyUnregisteredError:
                logging.warning("Authorization key not found or invalid. Re-authenticating...")
                await self.authenticate_client_via_msg()
                retry_count += 1

            except asyncio.CancelledError:
                logging.error("Client task cancelled, exiting run_client.")
                break  # Exit loop if cancelled

            except Exception as e:
                logging.error(f"An error occurred: {e}")
                retry_count += 1
                await asyncio.sleep(5)  # Wait before retrying

        if retry_count >= max_retries:
            logging.error("Max retries reached. Could not start the client.")

    async def send_message(self, receiver, message):
        try:
            await self.client.connect()
            self.handle_routes(self.client)

            await self.client.send_message(receiver, message)

            logging.info(f'Message sent: {message}')
        except errors.AuthKeyUnregisteredError:
            logging.warning("Authorization key not found or invalid. Re-authenticating...")
            await self.authenticate_client_via_msg()
            await self.send_message(receiver, message)  # Retry sending the message after re-authentication

    async def send_audio(self, receiver, audiofile_path):
        try:
            await self.client.connect()
            self.handle_routes(self.client)
            if await self.client.is_user_authorized():
                if audiofile_path and os.path.exists(audiofile_path):
                    logging.info("Audio file found!")
                    await self.client.send_file(receiver, audiofile_path)
                else:
                    logging.warning(f"Audio file {audiofile_path} does not exist.")
        except errors.AuthKeyUnregisteredError:
            logging.warning("Authorization key not found or invalid. Re-authenticating...")
            await self.authenticate_client_via_msg()
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
        logging.info('Client disconnected')

    async def authenticate_client_via_msg(self, counter=None):
        """Authenticate the client by sending a code request and waiting for the code."""
        await self.client.connect()
        if counter is None or counter <= 1:
            self.auth_event.set()  # Set the event to alert to the background thread that authentication is needed.

            try:
                self.phone_hash = await self.client.send_code_request(self.phone_number)
                while self.auth_code is None:
                    if not self.auth_event.is_set():
                        self.auth_event.set()
                    logging.info("from authenticate_client_via_msg --> auth_code is None. Waiting")
                    await asyncio.sleep(3)  # Non-blocking sleep

                await self.client.sign_in(self.phone_number, self.auth_code)
                logging.info("from authenticate_client_via_msg --> sign in request is sent.")

            except asyncio.CancelledError:
                logging.error("Authentication task cancelled.")
                # Handle cancellation if necessary
                return
            except Exception as e:
                logging.error(f"Error from authenticate_client_via_msg --> {e}")
        else:
            logging.info(f"Waiting for the client to send the authentication code... (Attempt {counter})")
            with self.client as client:
                result = client(functions.auth.ResendCodeRequest(
                    phone_number=self.phone_number,
                    phone_code_hash=self.phone_hash,
                    reason='some string here'
                ))
                logging.info(f'from authenticate_client_via_msg --> result.stringify() = {result.stringify()}')

    def flush(self):
        self.client = None
        self.loop = None
        self.messages_received = []
        self.phone_hash = None
