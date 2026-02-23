def test_relative_date_resolution(preprocessor):
    text = "amanha as 14h houve um incidente"
    result = preprocessor.preprocess(text)

    assert "2026-02-24" in result["cleaned_text"]
    assert result["hints"]["reference_date"] == "2026-02-24"


def test_invalid_hour_detection(preprocessor):
    text = "ocorreu um erro as 73h no sistema"
    result = preprocessor.preprocess(text)

    assert "INVALIDO" in result["cleaned_text"]
    assert result["hints"]["normalized_time"] == "INVALIDO"


def test_accent_and_case_normalization(preprocessor):
    text = "Amanhã Às 14h No Escritório"
    result = preprocessor.preprocess(text)

    assert result["cleaned_text"] == "2026-02-24 as 14:00 no escritorio"


def test_written_date_with_fuzzy_month(preprocessor):
    text = "ocorreu em 5 de feverero de 2025"
    result = preprocessor.preprocess(text)

    assert "2025-02-05" in result["cleaned_text"]
    assert result["hints"]["normalized_written_date"] == "2025-02-05"