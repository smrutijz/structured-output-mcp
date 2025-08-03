from __future__ import annotations
from typing import Any, Annotated, List, Type, Union
from datetime import date
from pydantic import BaseModel, Field, ConfigDict


def create_extraction_model(extract_type: Type[Any], extract_description: str):
    """
    Dynamically build an Extraction model for the given `extract_type` with a user-friendly prompt
    as description. The `value` field can be:
      - A scalar of `extract_type` (e.g. str, date, float, etc.)
      - A list of those
      - A nested dict (any JSON object)

    The order of types ensures list inputs are matched before scalar types, to avoid string coercion
    quirks in Pydantic's union validation. See related notes: https://stackoverflow.com/q/78352905 :contentReference[oaicite:1]{index=1}
    """
    # Union type: List first, then extract_type, then dict for JSON
    value_annotation = Annotated[
        Union[
            List[extract_type],
            extract_type,
            dict[str, Any],
            None
        ],
        Field(
            ...,
            description=extract_description,
            union_mode="left_to_right"
        ),
    ]

    class Extraction(BaseModel):
        model_config = ConfigDict(strict=True)  # Required to honor strict type checking

        value: value_annotation
        context: List[str] = Field(
            ...,
            description=(
                "A list of strings providing the context of the extraction, "
                "such as the document name and/or section of the input text."
            )
        )

    return Extraction
