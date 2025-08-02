from typing import TypedDict
from datetime import date
from langchain_openai import ChatOpenAI
from schema_builder import create_extraction_model


# 1. Dynamically create your "ResponseFormatter" using your model
#    At runtime, you pass the user prompt (description) to generate the model.
ExtractionModel = create_extraction_model(
    extract_type=Union[str, date, float],                   # e.g. your union types
    user_prompt="Please provide the cell organelle that produces ATP"
)

# 2. Bind the model as a 'tool' directly to the LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_with_extraction = llm.bind_tools(
    [ExtractionModel],
    tool_choice="auto"         # Let the model decide when to use it
)

# 3. Invoke the LLM — LangChain will prompt with the tool as a "function"
ai_msg = llm_with_extraction.invoke("What is the powerhouse of the cell?")

# 4. Inspect the tool-call arguments as a Python dict
tool_call = ai_msg.tool_calls[0]
raw_args: TypedDict = tool_call["args"]
print("tool args →", raw_args)

# 5. Parse into your Pydantic model for extra validation
structured_response = ExtractionModel.model_validate(raw_args)
print("parsed object →", structured_response)

# 6. Access values in strongly‐typed fashion
print("value:", structured_response.value)
print("context:", structured_response.context)






import os
import json
import logging
from mcp.server.fastmcp import FastMCP
from schema_builder import create_extraction_model

from langchain_openai import ChatOpenAI


# ---- Configuration ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY in .env or env")

# MCP server with name "Extractor"
mcp = FastMCP("Extractor")
logging.basicConfig(level=logging.INFO)

# ---- Model & base prompt ----
llm = ChatOpenAI(temperature=0.0, openai_api_key=OPENAI_API_KEY)

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
def extract(text: str, extract_type, user_prompt) -> dict:
    """
    fields_schema: e.g. {"name": "str", "age": "int", "location": "str"}
    """
    # Build dynamic Pydantic model
    ExtractionModel = create_extraction_model(
        extract_type=Union[str, date, float],                   # e.g. your union types
        user_prompt="Please provide the cell organelle that produces ATP"
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    llm_with_extraction = llm.bind_tools(
        [ExtractionModel],
        tool_choice="auto"
    )

    # # Create a structured output runnable
    # chain = create_structured_output_runnable(
    #     prompt=extract_prompt,
    #     output_schema=ExtractionModel,
    #     llm=llm,
    #     mode="openai-json",  # Uses OpenAI JSON mode for strict schema enforcement
    # )
    inputs = {"text": text, "fields_schema_json": json.dumps(fields_schema)}
    out = chain(inputs)  # May raise on parsing error
    return out

if __name__ == "__main__":
    # Use Streamable‑HTTP transport so it's available at http://localhost:8000/mcp
    mcp.run(transport="streamable‑http", host="0.0.0.0", port=8000)
