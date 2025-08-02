# test_extraction.py

from datetime import date
import pytest
from schema_builder import create_extraction_model


def test_text_str():
    ExtractionModel = create_extraction_model(str, "Extracted email address from the document.")
    inst = ExtractionModel(
        value="user@example.com",
        context=["Document: Invoice #1234", "Section: Billing Information"]
    )
    assert inst.value == "user@example.com"
    assert inst.context == ["Document: Invoice #1234", "Section: Billing Information"]


def test_text_date():
    ExtractionModel = create_extraction_model(date, "Extracted date from the document.")
    inst = ExtractionModel(
        value=date(2025, 8, 2),
        context=["Document: Invoice #1234", "Section: Billing Information"]
    )
    assert inst.value == date(2025, 8, 2)
    assert inst.context == ["Document: Invoice #1234", "Section: Billing Information"]


def test_json_nested():
    # Use dict as extract_type to accept any JSON-like object
    ExtractionModel = create_extraction_model(dict, "Extracted JSON structure.")
    payload = {
        "email": "user@example.com",
        "details": {"name": "John Doe", "age": 30}
    }
    inst = ExtractionModel(
        value=payload,
        context=["Document: User Profile", "Section: Personal Information"]
    )
    assert inst.value == payload
    assert inst.context == ["Document: User Profile", "Section: Personal Information"]


def test_list_str():
    ExtractionModel = create_extraction_model(str, "Extracted multiple string items.")
    inst = ExtractionModel(
        value=["user@example.com", "admin@example.com"],
        context=["Document: User List", "Section: Contacts"]
    )
    assert inst.value == ["user@example.com", "admin@example.com"]
    assert inst.context == ["Document: User List", "Section: Contacts"]
