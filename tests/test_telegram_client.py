import asyncio
import threading
from unittest.mock import AsyncMock, patch

from app.Server.LLM.llm_chat_tools.telegramclienthandler import TelegramClientHandler
import pytest
import os

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv('TELEGRAM_CLIENT_APP_ID')
CLIENT_HASH = os.getenv('TELEGRAM_CLIENT_APP_HASH')
CLIENT_PHONE_NUMBER = os.getenv('TELEGRAM_CLIENT_PHONE_NUMBER')
auth_event = threading.Event()


@pytest.fixture
async def client():
    with patch('builtins.input', return_value='12345'):
        with patch("app.Server.LLM.llm_chat_tools.telegramclienthandler.TelegramClientHandler.initialize_client",
                   new_callable=AsyncMock):
            client_instance = TelegramClientHandler(
                app_id=CLIENT_ID,
                app_hash=CLIENT_HASH,
                phone_number=CLIENT_PHONE_NUMBER,
                auth_event=auth_event
            )

            with client_instance:
                with patch('builtins.input', return_value='12345'):
                    code = input("Enter code: ")
                    assert code is not None
                    yield client_instance
                await client_instance.stop_client()
                await client_instance.flush()


@pytest.mark.asyncio
async def test_telegram_client(client):
    assert client.client_connected is True


@pytest.mark.asyncio
async def test_telegram_send_message(client):
    with patch("app.Server.LLM.llm_chat_tools.telegramclienthandler.TelegramClientHandler.send_message",
               new_callable=AsyncMock) as mock_send_message:
        assert client.client_connected is True
        await client.send_message("DeceptifyBot", "This is a test message")
        mock_send_message.assert_called_once_with("DeceptifyBot", "This is a test message")

        assert client.messages_received is not None
        assert isinstance(client.messages_sent[-1], tuple)
        assert client.messages_sent[-1][0] == "DeceptifyBot"
        assert client.messages_sent[-1][1] == "This is a test message"


@pytest.mark.asyncio
async def test_telegram_send_audio(client):
    with patch("app.Server.LLM.llm_chat_tools.telegramclienthandler.TelegramClientHandler.send_audio",
               new_callable=AsyncMock) as mock_send_audio:
        assert client.client_connected is True
        await client.send_audio("DeceptifyBot", 'tests/files/test.mp3')
        mock_send_audio.assert_called_once_with("DeceptifyBot", 'tests/files/test.mp3')


@pytest.mark.asyncio
async def test_telegram_stop_client(client):
    with patch("app.Server.LLM.llm_chat_tools.telegramclienthandler.TelegramClientHandler.stop_client",
               new_callable=AsyncMock) as mock_stop_client:
        assert client.client_connected is True
        await client.stop_client()
        mock_stop_client.assert_called_once()
        assert client.client_connected is False


@pytest.mark.asyncio
async def test_telegram_authentication_twice(client):
    with patch("app.Server.LLM.llm_chat_tools.telegramclienthandler.TelegramClientHandler.authenticate_client_via_msg",
               new_callable=AsyncMock) as mock_authentication:
        assert client.client_connected is True
        mock_authentication.return_value = "User is already authorized, you can connect and run the program..."
        res = await client.authenticate_client_via_msg()
        assert res == "User is already authorized, you can connect and run the program..."


@pytest.mark.asyncio
async def test_telegram_make_event_loop(client):
    with patch("app.Server.LLM.llm_chat_tools.telegramclienthandler.TelegramClientHandler.make_event_loop",
               new_callable=AsyncMock) as mock_loop:
        assert client.client_connected is True
        await client.make_event_loop()

        mock_loop.assert_called_once()
        assert client.loop is not None
        assert client.loop is asyncio.get_event_loop()
