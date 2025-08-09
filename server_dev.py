import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from schema_builder import create_extraction_model
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
    port="8000"
    )
logging.basicConfig(level=logging.INFO)


llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)

extract_prompt = PromptTemplate(
    template=(
        "You are a JSON extractor. Given `text` and a list of field-names, "
        "extract values for each field from the text. If a field is not found, use null. "
        "Respond with strict JSON matching the schema, no extra keys."
    ),
    input_variables=["text", "fields_schema_json"]
)

# ---- MCP tool ----
@mcp.tool()
def extract(text: str, user_prompt, extract_description: str, extract_type) -> dict:
    """
    
    """
    ExtractionModel = create_extraction_model(extract_type, extract_description)

    # Create a structured output runnable
    chain = create_structured_output_runnable(
        prompt=extract_prompt,
        output_schema=ExtractionModel,
        llm=llm,
        mode="openai-json",  # Uses OpenAI JSON mode for strict schema enforcement
    )
    inputs = {"text": text, "fields_schema_json": json.dumps(fields_schema)}
    out = chain(inputs)  # May raise on parsing error
    return out

if __name__ == "__main__":
    # Use Streamable‑HTTP transport so it's available at http://localhost:8000/mcp
    mcp.run(transport="streamable‑http", host="0.0.0.0", port=8000)
