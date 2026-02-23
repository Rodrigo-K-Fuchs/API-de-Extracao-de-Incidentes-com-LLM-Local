import json
from core.incident_extractor import IncidentExtractor
from model.incident import Incident


def fake_llm(_):
    return json.dumps({
        "data_ocorrencia": "2026-02-23 14:00",
        "local": "escritorio de sao paulo",
        "tipo_incidente": "falha no servidor",
        "impacto": "sistema fora do ar"
    })


def test_incident_extractor_with_mocked_llm():

    extractor = IncidentExtractor(llm=fake_llm)

    incidente = extractor.extract(
        "Houve uma falha no servidor no escritório de São Paulo às 14h"
    )

    assert isinstance(incidente, Incident)
    assert incidente.local == "escritorio de sao paulo"
    assert incidente.tipo_incidente == "falha no servidor"
    assert incidente.impacto == "sistema fora do ar"