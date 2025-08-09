import asyncio
from fastmcp.client.transports import SSETransport
from fastmcp import Client
import json

async def main():
    transport = SSETransport(url="http://127.0.0.1:8000/sse")
    # transport = SSETransport(url="https://mcp-structured-output-gxeyaucgcfe3a0gf.southeastasia-01.azurewebsites.net/sse")
    async with Client(transport) as client:
        resp = await client.call_tool(
            "extract",
            arguments={
                # "text": "My email id is smrutijz@hotmail.com",
                # "text": "My email id is smrutijz@hotmail.com, my backup is smruti.singapore@gmail.com",
                "text": "There is no email here.",
                "user_prompt": "Extract the email address",
                "sys_prompt": "You are a data extraction assistant.\nYour only task is to find valid email addresses in the user‑provided text. Do not add any other commentary.",
                "extract_description": "Email address",
                "extract_type": "str"
            }
        )

        # Extract the JSON text from resp.content
        first_cb_text = None
        for cb in resp.content:
            first_cb_text = getattr(cb, "text", None)
            if first_cb_text:
                break
        
        if not first_cb_text:
            print("No extraction content found.")
            return
        
        # Parse JSON string to dict
        extracted_json = json.loads(first_cb_text)
        extracted_email = extracted_json.get("value")
        
        print("Extracted email:", extracted_email)

if __name__ == "__main__":
    asyncio.run(main())
