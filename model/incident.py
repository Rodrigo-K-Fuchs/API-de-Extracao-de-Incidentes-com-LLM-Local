from typing import Optional
from pydantic import BaseModel, Field


class Incident(BaseModel):
    """
    Modelo Pydantic que representa os dados estruturados de um incidente
    extraído a partir de texto livre pelo LLM.

    Todos os campos são opcionais e devem ser preenchidos apenas quando
    a informação puder ser inferida com segurança a partir do texto original.
    """

    data_ocorrencia: Optional[str] = Field(
        default=None,
        description=(
            "Data e hora do ocorrido no formato YYYY-MM-DD HH:MM. "
            'Use "INVALIDO" se houver hora impossível no texto.'
        ),
    )

    local: Optional[str] = Field(
        default=None,
        description="Cidade, local público ou referência espacial mencionada",
    )

    tipo_incidente: Optional[str] = Field(
        default=None,
        description="Descrição resumida do que aconteceu",
    )

    impacto: Optional[str] = Field(
        default=None,
        description="Consequência do incidente ou sistemas afetados",
    )