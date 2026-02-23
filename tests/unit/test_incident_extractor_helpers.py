from core.incident_extractor import IncidentExtractor


def test_fix_invalid_time_detects_invalid_hour():
    extractor = IncidentExtractor()
    result = extractor._fix_invalid_time(
        data_ocorrencia="2026-02-23 14:00",
        original_text="erro ocorrido as 99h"
    )

    assert result == "INVALIDO"


def test_fix_invalid_time_keeps_valid():
    extractor = IncidentExtractor()
    result = extractor._fix_invalid_time(
        data_ocorrencia="2026-02-23 14:00",
        original_text="erro ocorrido as 14h"
    )

    assert result == "2026-02-23 14:00"