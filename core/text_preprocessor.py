import re
import unicodedata
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple


def _levenshtein_distance(a: str, b: str) -> int:
    """
    Calcula a distância de Levenshtein entre duas strings.

    Args:
        a: Primeira string.
        b: Segunda string.

    Returns:
        Número inteiro representando o número mínimo de operações
        de inserção, remoção ou substituição para transformar 'a' em 'b'.
    """
    len_b = len(b)
    previous = list(range(len_b + 1))

    for i, char_a in enumerate(a, start=1):
        current = [i] + [0] * len_b
        for j, char_b in enumerate(b, start=1):
            if char_a == char_b:
                current[j] = previous[j - 1]
            else:
                current[j] = 1 + min(previous[j], current[j - 1], previous[j - 1])
        previous = current

    return previous[len_b]


def _max_distance(word: str) -> int:
    """
    Define a distância máxima de edição tolerada para o match fuzzy,
    proporcional ao tamanho da palavra.

    Args:
        word: Palavra de referência para calcular o limiar.

    Returns:
        Distância máxima permitida: 1 para palavras curtas (≤4 chars),
        2 para médias (≤7 chars) e 3 para longas.
    """
    length = len(word)
    if length <= 4:
        return 1
    if length <= 7:
        return 2
    return 3


def _fuzzy_match(token: str, vocabulary: Dict[str, Any]) -> Optional[str]:
    """
    Tenta encontrar a chave mais próxima de um token dentro de um vocabulário,
    usando distância de Levenshtein com limiar adaptativo.

    A busca aplica dois filtros de pré-seleção para eficiência: diferença de
    comprimento maior que 1 e primeira letra diferente descartam o candidato
    imediatamente.

    Args:
        token: Palavra a ser pesquisada no vocabulário.
        vocabulary: Dicionário cujas chaves são os termos válidos.

    Returns:
        A chave do vocabulário mais próxima ao token dentro do limiar permitido,
        ou None se nenhuma correspondência for encontrada.
    """
    if token in vocabulary:
        return token

    best_key: Optional[str] = None
    best_distance = float("inf")

    for key in vocabulary:
        if abs(len(token) - len(key)) > 1:
            continue

        if token[0] != key[0]:
            continue

        threshold = _max_distance(min(token, key, key=len))
        distance = _levenshtein_distance(token, key)

        if distance <= threshold and distance < best_distance:
            best_distance = distance
            best_key = key

    return best_key


class TextPreprocessor:
    """
    Pré-processa textos em português antes de enviá-los ao LLM, realizando
    limpeza, normalização e extração de hints temporais.

    O pré-processamento inclui normalização Unicode, remoção de acentos,
    limpeza de caracteres de controle e pontuação, além da resolução de
    expressões de data relativas (ex.: 'ontem', 'amanhã'), normalização de
    horários (ex.: '14h30') e datas escritas por extenso (ex.: '3 de abril de 2024').

    Os hints extraídos durante o processo são retornados junto ao texto limpo
    para auxiliar o LLM na interpretação das informações temporais.
    """

    RELATIVE_DATE_MAP: Dict[str, int] = {
        "amanha": 1,
        "hoje": 0,
        "ontem": -1,
        "anteontem": -2,
        "ante-ontem": -2,
    }

    TIME_PATTERN = re.compile(
        r"(?<!\d)(?<!por\s)(\b\d{1,2})\s*[hH](?:oras?)?\s*(\d{0,2})\b"
    )

    WRITTEN_DATE_PATTERN = re.compile(
        r"\b(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\b",
        re.IGNORECASE,
    )

    MONTH_MAP: Dict[str, str] = {
        "janeiro": "01",
        "fevereiro": "02",
        "marco": "03",
        "abril": "04",
        "maio": "05",
        "junho": "06",
        "julho": "07",
        "agosto": "08",
        "setembro": "09",
        "outubro": "10",
        "novembro": "11",
        "dezembro": "12",
    }

    def __init__(self, reference_date: Optional[datetime] = None):
        """
        Inicializa o TextPreprocessor com uma data de referência para resolução
        de expressões temporais relativas.

        Args:
            reference_date: Data base para calcular expressões como 'ontem' ou
                            'amanhã'. Se não fornecida, utiliza o momento atual.
        """
        self.reference_date = reference_date or datetime.now()

    def preprocess(self, text: str) -> Dict[str, Any]:
        """
        Executa o pipeline completo de pré-processamento sobre o texto de entrada.

        As etapas aplicadas em ordem são: normalização Unicode, remoção de acentos,
        conversão para minúsculas, remoção de caracteres de controle, correção de
        espaços, resolução de datas relativas, normalização de horários, normalização
        de datas escritas por extenso e normalização de pontuação.

        Args:
            text: Texto bruto a ser processado.

        Returns:
            Dicionário contendo:
                - 'cleaned_text': texto normalizado e limpo.
                - 'hints': dicionário com informações temporais pré-extraídas,
                  podendo conter as chaves 'reference_date', 'normalized_time'
                  e/ou 'normalized_written_date'.
        """
        text = self._normalize_unicode(text)
        text = self._remove_accents(text)
        text = text.lower()
        text = self._remove_control_chars(text)
        text = self._fix_whitespace(text)

        hints: Dict[str, str] = {}

        text, date_hint = self._resolve_relative_dates(text)
        if date_hint:
            hints["reference_date"] = date_hint

        text, time_hint = self._normalize_time_expressions(text)
        if time_hint:
            hints["normalized_time"] = time_hint

        text, written_date_hint = self._normalize_written_dates(text)
        if written_date_hint:
            hints["normalized_written_date"] = written_date_hint

        text = self._normalize_punctuation(text)
        text = self._fix_whitespace(text)

        return {
            "cleaned_text": text.strip(),
            "hints": hints,
        }

    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """Aplica normalização NFC ao texto para garantir representação Unicode consistente."""
        return unicodedata.normalize("NFC", text)

    @staticmethod
    def _remove_accents(text: str) -> str:
        """Remove acentos e diacríticos do texto via decomposição NFKD."""
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def _remove_control_chars(text: str) -> str:
        """Remove caracteres de controle ASCII invisíveis, preservando quebras de linha."""
        return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    @staticmethod
    def _fix_whitespace(text: str) -> str:
        """
        Corrige espaçamentos excessivos, colapsando múltiplas quebras de linha,
        espaços/tabs repetidos e espaços antes de pontuação.
        """
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" ([.,;:!?])", r"\1", text)
        return text

    @staticmethod
    def _normalize_punctuation(text: str) -> str:
        """Substitui aspas tipográficas e travessões Unicode por equivalentes ASCII."""
        text = re.sub(r"[\u201c\u201d\u201e]", '"', text)
        text = re.sub(r"[\u2018\u2019\u201a]", "'", text)
        text = re.sub(r"\s*[\u2013\u2014]\s*", " - ", text)
        return text

    def _resolve_relative_dates(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Localiza expressões de data relativas no texto (ex.: 'ontem', 'amanhã')
        usando match fuzzy e as substitui pela data absoluta correspondente no
        formato YYYY-MM-DD, calculada a partir de reference_date.

        Args:
            text: Texto já normalizado (sem acentos, em minúsculas).

        Returns:
            Tupla com o texto modificado e a data resolvida como string
            no formato YYYY-MM-DD, ou None se nenhuma expressão for encontrada.
        """
        tokens = text.split()
        resolved_date: Optional[str] = None
        result_tokens = []

        for token in tokens:
            clean_token = re.sub(r"[^\w-]", "", token)

            if resolved_date is None:
                matched_key = _fuzzy_match(clean_token, self.RELATIVE_DATE_MAP)

                if matched_key:
                    delta = self.RELATIVE_DATE_MAP[matched_key]
                    resolved = self.reference_date + timedelta(days=delta)
                    resolved_date = resolved.strftime("%Y-%m-%d")
                    token = token.replace(clean_token, resolved_date)

            result_tokens.append(token)

        return " ".join(result_tokens), resolved_date

    def _normalize_time_expressions(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Converte expressões de horário no formato '14h30' ou '9h' para o padrão
        'HH:MM', substituindo-as diretamente no texto. Horários com valores
        impossíveis (hora > 23 ou minuto > 59) são substituídos por 'INVALIDO'.

        Args:
            text: Texto a ser processado.

        Returns:
            Tupla com o texto modificado e o último horário normalizado encontrado
            (ou 'INVALIDO' em caso de valor impossível), ou None se nenhum for encontrado.
        """
        hint: Optional[str] = None

        def replacer(m: re.Match) -> str:
            nonlocal hint
            hour = int(m.group(1))
            minute = int(m.group(2) or 0)

            if hour > 23 or minute > 59:
                hint = "INVALIDO"
                return "INVALIDO"

            hint = f"{hour:02d}:{minute:02d}"
            return hint

        text = self.TIME_PATTERN.sub(replacer, text)
        text = re.sub(r"(INVALIDO|\d{2}:\d{2})(?=\S)", r"\1 ", text)

        return text, hint

    def _normalize_written_dates(self, text: str) -> Tuple[str, Optional[str]]:
        """
        Converte datas escritas por extenso no formato 'DD de mês de AAAA'
        para o padrão ISO 'YYYY-MM-DD', substituindo-as no texto.
        O nome do mês é resolvido com match fuzzy para tolerar pequenos erros ortográficos.

        Args:
            text: Texto a ser processado.

        Returns:
            Tupla com o texto modificado e a data normalizada no formato YYYY-MM-DD,
            ou None se nenhuma data por extenso for encontrada.
        """
        hint: Optional[str] = None

        def replacer(m: re.Match) -> str:
            nonlocal hint
            day = m.group(1).zfill(2)
            raw_month = m.group(2).lower()
            year = m.group(3)

            month = _fuzzy_match(raw_month, self.MONTH_MAP)
            if not month:
                return m.group(0)

            hint = f"{year}-{self.MONTH_MAP[month]}-{day}"
            return hint

        text = self.WRITTEN_DATE_PATTERN.sub(replacer, text)
        return text, hint