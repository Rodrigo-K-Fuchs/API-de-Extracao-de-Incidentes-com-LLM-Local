from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

from core.incident_extractor import IncidentExtractor

app = FastAPI(title="Incident Extraction API")

extractor = IncidentExtractor(
    model="llama3.2",
    reference_date=datetime.now(),
)


class IncidentRequest(BaseModel):
    """Payload de entrada para o endpoint de extração de incidentes."""

    texto: str


@app.post("/extract")
def extract_incident(request: IncidentRequest):
    """
    Recebe um texto livre descrevendo um incidente e retorna os dados
    estruturados extraídos pelo LLM.

    Args:
        request: Objeto contendo o campo 'texto' com o relato do incidente.

    Returns:
        JSON com os campos do incidente extraído (data_ocorrencia,
        local, tipo_incidente, impacto).

    Raises:
        HTTPException 400: Caso o texto enviado esteja vazio.
    """
    if not request.texto.strip():
        raise HTTPException(status_code=400, detail="Texto vazio")

    incidente = extractor.extract(request.texto)
    return incidente.model_dump()