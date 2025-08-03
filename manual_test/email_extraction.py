import pytest
import asyncio
import subprocess
import time
from fastmcp.client.transports import SSETransport
from fastmcp import Client
import json
import re

pytestmark = pytest.mark.asyncio  # Enable async tests


@pytest.fixture(scope="module", autouse=True)
def start_server():
    server = subprocess.Popen(["python", "server.py"])
    time.sleep(5)
    yield
    server.terminate()
    server.wait()


async def get_extraction_value(resp):
    first_cb_text = None
    for cb in resp.content:
        first_cb_text = getattr(cb, "text", None)
        if first_cb_text:
            break
    if not first_cb_text:
        pytest.fail("No content text found in response")
    try:
        parsed = json.loads(first_cb_text)
        return parsed.get("value", None)
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from response text: {first_cb_text}\nError: {e}")


async def test_single_email_extraction():
    transport = SSETransport(url="http://127.0.0.1:8000/sse")
    async with Client(transport) as client:
        resp = await client.call_tool(
            "extract",
            arguments={
                "text": "My email is smrutijz@hotmail.com",
                "user_prompt": "Extract the email address",
                "sys_prompt": "You are a data extraction assistant.\nYour only task is to find valid email addresses in the user‑provided text. Do not add any other commentary.",
                "extract_description": "Email address",
                "extract_type": "str"
            }
        )
        value = await get_extraction_value(resp)
        assert value == "smrutijz@hotmail.com"
        assert isinstance(value, str)
        assert re.fullmatch(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}", value)


async def test_multiple_email_extraction():
    transport = SSETransport(url="http://127.0.0.1:8000/sse")
    async with Client(transport) as client:
        resp = await client.call_tool(
            "extract",
            arguments={
                "text": "My email is smrutijz@hotmail.com and backup is smruti.singapore@gmail.com",
                "user_prompt": "Extract the email address",
                "sys_prompt": "You are a data extraction assistant.\nYour only task is to find valid email addresses in the user‑provided text. Do not add any other commentary.",
                "extract_description": "Email address",
                "extract_type": "str"
            }
        )
        value = await get_extraction_value(resp)
        assert isinstance(value, list), "Expected list of emails"
        assert len(value) == 2
        for email in value:
            assert re.fullmatch(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}", email)


async def test_no_email_present():
    transport = SSETransport(url="http://127.0.0.1:8000/sse")
    async with Client(transport) as client:
        resp = await client.call_tool(
            "extract",
            arguments={
                "text": "There is no email here.",
                "user_prompt": "Extract the email address",
                "sys_prompt": "You are a data extraction assistant.\nYour only task is to find valid email addresses in the user‑provided text. Do not add any other commentary.",
                "extract_description": "Email address",
                "extract_type": "str"
            }
        )
        value = await get_extraction_value(resp)
        assert value is None or value == "null" or value == "", f"Expected null/None/empty, got: {value}"
