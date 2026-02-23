from model.incident import Incident


def test_incident_model_accepts_partial_data():
    incident = Incident(
        local="praca sete",
        tipo_incidente="queda"
    )

    assert incident.local == "praca sete"
    assert incident.tipo_incidente == "queda"
    assert incident.data_ocorrencia is None
    assert incident.impacto is None


def test_incident_invalid_time():
    incident = Incident(data_ocorrencia="INVALIDO")
    assert incident.data_ocorrencia == "INVALIDO"