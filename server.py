import os
import logging
from mcp.server.fastmcp import FastMCP
from schema_builder import create_extraction_model
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# ---- Configuration ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY in .env or env")

OPENAI_MODEL = os.getenv("OPENAI_MODEL")
if not OPENAI_MODEL:
    raise RuntimeError("Please set OPENAI_MODEL in .env or env")

# MCP server
mcp = FastMCP(
    "Extractor",
    host="0.0.0.0",
    port="8000",
    stateless_http=False
    )
logging.basicConfig(level=logging.INFO)

# ---- MCP tool ----
@mcp.tool()
def extract(text: str, user_prompt: str, sys_prompt: str, extract_description: str, extract_type: str = "str") -> dict:
    """
    description: Extracts structured data from text based on a dynamic schema.
    text: The input text from which to extract data.
    user_prompt: A prompt to guide the extraction process.
    sys_prompt: A system message to provide context for the extraction.
    extract_type: The type of data to extract (e.g., str, date, float).
    """
    ExtractionModel = create_extraction_model(extract_type, extract_description)

    llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

    llm_with_structured_extraction = llm.bind_tools(
        [ExtractionModel],
        tool_choice="auto"
    )

    msg = llm_with_structured_extraction.invoke([
        SystemMessage(content=sys_prompt),
        HumanMessage(content=f"{user_prompt}:\nfrom the following user text:\n{text}")
    ])

    if hasattr(msg, "tool_calls") and msg.tool_calls and isinstance(msg.tool_calls, list):
        return msg.tool_calls[0]["args"]
    else:
        return {
            "error": "Tool call failed. No structured output was returned by the model."
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
