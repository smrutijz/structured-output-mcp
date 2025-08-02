import asyncio
from fastmcp.client.transports import SSETransport
from fastmcp import Client

async def main():
    transport = SSETransport(url="http://127.0.0.1:8000/sse")
    async with Client(transport) as client:
        resp = await client.call_tool(
            "extract",
            arguments={
                "text": "My email id is smrutijz@hotmail.com",
                "user_prompt": "Extract the email address",
                "sys_prompt": (
                    "You are a JSON extractor. Given `text` and field‑names, "
                    "extract values. If not found, return null. "
                    "Respond with strict JSON—no extra keys."
                ),
                "extract_description": "Email address",
                "extract_type": "str"
            }
        )
    print("resp.data:", resp.data)
    print("resp.structured_content:", resp.structured_content)
    for cb in resp.content:
        print("Text content:", getattr(cb, "text", None))

if __name__ == "__main__":
    asyncio.run(main())