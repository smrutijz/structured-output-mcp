import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async def main():
    url = "http://localhost:8000/mcp"
    async with streamablehttp_client(url) as (reader, writer, _) :
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            # 🚀 Your specific payload with email extraction
            result = await session.call_tool(
                "extract",
                arguments={
                    "text": "My email id is smrutijz@hotmail.com",
                    "user_prompt": "Extract the email address from the user input text",
                    "sys_prompt": (
                        "You are a JSON extractor. Given `text` and a list of field‑names, "
                        "extract values from the text. If a field is not found, return null. "
                        "Respond with strict JSON matching the schema—no extra keys."
                    ),
                    "extract_description": "Email address",
                    "extract_type": "str"
                }
            )

            print("✅ MCP response →", result.json())

if __name__ == "__main__":
    asyncio.run(main())
