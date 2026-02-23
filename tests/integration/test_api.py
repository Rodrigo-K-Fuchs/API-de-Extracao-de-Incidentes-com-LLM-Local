from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_api_extract_success(monkeypatch):
    from core.incident_extractor import IncidentExtractor
    from model.incident import Incident

    def fake_extract(self, text):
        return Incident(
            data_ocorrencia="2026-02-23 14:00",
            local="bh",
            tipo_incidente="queda",
            impacto="pe quebrado"
        )

    monkeypatch.setattr(IncidentExtractor, "extract", fake_extract)

    response = client.post(
        "/extract",
        json={"texto": "tropecei na praca sete as 14h"}
    )

    assert response.status_code == 200
    body = response.json()

    assert body["local"] == "bh"
    assert body["impacto"] == "pe quebrado"


def test_api_empty_text():
    response = client.post(
        "/extract",
        json={"texto": "   "}
    )

    assert response.status_code == 400