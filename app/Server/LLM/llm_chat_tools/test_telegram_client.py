import asyncio
import threading
from contextlib import asynccontextmanager
from app.Server.LLM.llm_chat_tools.telegramclienthandler import TelegramClientHandler
import pytest
import os

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('TELEGRAM_CLIENT_APP_ID')
CLIENT_HASH = os.getenv('TELEGRAM_CLIENT_APP_HASH')
CLIENT_PHONE_NUMBER = os.getenv('TELEGRAM_CLIENT_PHONE_NUMBER')
auth_event = threading.Event()


@asynccontextmanager
async def lifespan():
    print("Starting up")
    client_instance = TelegramClientHandler(
        app_id=CLIENT_ID,
        app_hash=CLIENT_HASH,
        phone_number=CLIENT_PHONE_NUMBER,
        auth_event=auth_event,
        is_test=True
    )

    while not client_instance.client_connected:
        print("in loop")
        await asyncio.sleep(1)

    try:
        yield client_instance
    finally:
        print("Client successfully send to test")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(name='client')
async def client():
    async with lifespan() as client_instance:
        yield client_instance


@pytest.mark.anyio
async def test_telegram_client(client):
    assert client.client_connected is True


@pytest.mark.anyio
async def test_telegram_send_message(client):
    assert client.client_connected is True
    await client.send_message("DeceptifyBot", "This is a test message")

    assert client.messages_received is not None
    assert isinstance(client.messages_sent[-1], tuple)
    assert client.messages_sent[-1][0] is "DeceptifyBot"
    assert client.messages_sent[-1][1] is "This is a test message"


@pytest.mark.anyio
async def test_telegram_send_audio(client):
    assert client.client_connected is True
    await client.send_audio("DeceptifyBot", 'tests/files/test.mp3')


@pytest.mark.anyio
async def test_telegram_stop_client(client):
    assert client.client_connected is True
    await client.stop_client()
    assert client.client_connected is False


@pytest.mark.anyio
async def test_telegram_authentication_twice(client):
    assert client.client_connected is True
    res = await client.authenticate_client_via_msg()
    assert "User is already authorized, you can connect and run the program..." in res


@pytest.mark.anyio
async def test_telegram_make_event_loop(client):
    assert client.client_connected is True
    await client.make_event_loop()

    assert client.loop is not None
    assert client.loop is asyncio.get_event_loop()
