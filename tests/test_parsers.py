import pytest
from pathlib import Path
from src.parsers.pdf_parser import BankPDFParser

def test_parse_itau_pdf_dummy(tmp_path):
    dummy_pdf = tmp_path / "dummy.pdf"
    dummy_pdf.write_text("Dummy PDF Content")
    
    metrics = BankPDFParser.parse_itau_pdf(dummy_pdf)
    assert isinstance(metrics, dict)
    assert metrics["banco"] == "Itaú"
    assert "lucro_liquido_recorrente_mi" in metrics
