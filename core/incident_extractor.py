from typing import Optional
from datetime import datetime
import re

from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

from core.text_preprocessor import TextPreprocessor
from model.incident import Incident
from model.incident_prompt import INCIDENT_PROMPT_TEMPLATE
import os

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

class IncidentExtractor:
    """
    Extrai informações estruturadas de incidentes a partir de textos não estruturados
    utilizando um modelo de linguagem (LLM) via Ollama.

    O fluxo de extração consiste em pré-processar o texto de entrada, montar um prompt
    com instruções e contexto, invocar o LLM e retornar o resultado como um objeto Incident.
    """

    def __init__(
        self,
        llm: OllamaLLM | None = None,
        model: str = "llama3.2",
        reference_date: Optional[datetime] = None,
        temperature: float = 0.0,
    ):
        """
        Inicializa o IncidentExtractor configurando o pré-processador de texto,
        o parser de saída, o LLM e a chain de extração.

        Args:
            llm: Instância do OllamaLLM a ser utilizada. Se não fornecida, uma nova
                 instância será criada com os parâmetros informados.
            model: Nome do modelo Ollama a ser carregado caso nenhum LLM seja fornecido.
            reference_date: Data de referência utilizada pelo pré-processador para
                            resolver expressões temporais relativas presentes no texto.
            temperature: Temperatura de geração do LLM. O valor padrão 0.0 garante
                         respostas determinísticas.
        """
        self.preprocessor = TextPreprocessor(reference_date=reference_date)

        self.parser = PydanticOutputParser(pydantic_object=Incident)

        self.llm = llm or OllamaLLM(
            model=model,
            base_url=OLLAMA_HOST,
            temperature=temperature,
            format="json"
        )

        self.prompt = PromptTemplate(
            template=INCIDENT_PROMPT_TEMPLATE,
            input_variables=["cleaned_text", "hints_block"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        self.chain = self.prompt | self.llm | self.parser

    def extract(self, text: str, extra_context: str = "") -> Incident:
        """
        Processa um texto e extrai as informações do incidente como um objeto Incident.

        Args:
            text: Texto bruto descrevendo o incidente.
            extra_context: Contexto adicional opcional que será anexado ao bloco de
                           hints enviado ao LLM.

        Returns:
            Objeto Incident populado com as informações extraídas do texto.

        Raises:
            RuntimeError: Caso ocorra qualquer falha durante a invocação da chain.
        """
        preprocessed = self.preprocessor.preprocess(text)

        try:
            incident: Incident = self.chain.invoke(
                {
                    "cleaned_text": preprocessed["cleaned_text"],
                    "hints_block": self._build_hints_block(
                        preprocessed["hints"], extra_context
                    ),
                }
            )

            incident.data_ocorrencia = self._fix_invalid_time(
                incident.data_ocorrencia, text
            )

            return incident

        except Exception as e:
            raise RuntimeError(
                f"Erro ao extrair incidente via Ollama: {e}"
            )

    def extract_dict(self, text: str, extra_context: str = "") -> dict:
        """
        Wrapper sobre extract() que retorna o resultado serializado como dicionário.

        Args:
            text: Texto bruto descrevendo o incidente.
            extra_context: Contexto adicional opcional repassado para extract().

        Returns:
            Dicionário com os campos do Incident extraído.
        """
        return self.extract(text, extra_context).model_dump()

    @staticmethod
    def _build_hints_block(hints: dict, extra_context: str) -> str:
        """
        Constrói o bloco de hints que será inserido no prompt enviado ao LLM,
        consolidando as informações pré-extraídas pelo pré-processador e o
        contexto adicional fornecido pelo chamador.

        Args:
            hints: Dicionário de pares chave-valor extraídos pelo TextPreprocessor.
            extra_context: String de contexto adicional a ser anexada ao bloco.

        Returns:
            String formatada com os hints e o contexto adicional, ou string vazia
            caso nenhuma informação esteja disponível.
        """
        if not hints and not extra_context:
            return ""

        lines = ["Informações pré-extraídas pelo sistema:"]
        for key, value in hints.items():
            lines.append(f"- {key}: {value}")

        if extra_context:
            lines.append(f"\nContexto adicional: {extra_context}")

        return "\n".join(lines)

    @staticmethod
    def _fix_invalid_time(
        data_ocorrencia: Optional[str],
        original_text: str,
    ) -> Optional[str]:
        """
        Garante comportamento determinístico caso o texto contenha horas impossíveis
        como '73h', '999h', etc., retornando 'INVALIDO' nesses casos.

        Args:
            data_ocorrencia: Valor de data/hora extraído pelo LLM.
            original_text: Texto original utilizado para detectar padrões de hora inválida.

        Returns:
            'INVALIDO' se um padrão de hora impossível for encontrado no texto,
            caso contrário retorna o valor original de data_ocorrencia.
        """
        invalid_hour_pattern = re.compile(r"\b([2-9]\d|\d{3,})h\b")

        if invalid_hour_pattern.search(original_text.lower()):
            return "INVALIDO"

        return data_ocorrencia